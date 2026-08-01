import os
import re
from functools import lru_cache
from sqlalchemy import create_engine, event

def test():
    print('hello')

# LiionDB now ships as a bundled SQLite file (database/dfndb.sqlite).
# The original Azure PostgreSQL server has been retired, so liiondb()
# connects to the local copy instead — no internet connection needed.

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'database', 'dfndb.sqlite')

# Ranges exported from Postgres numrange columns look like '[283.0, 333.0]'
_RANGE_RE = re.compile(r'^\s*[\[\(]\s*([^,]+)\s*,\s*([^\]\)]+)\s*[\]\)]\s*$')

def _range_bound(value, index):
    '''Parse a '[lo, hi]' range string and return the requested bound as a
    float, or None if the bound is missing/nan. Non-range strings return None
    so lower()/upper() can fall back to normal string case conversion.'''
    if not isinstance(value, str):
        return None
    match = _RANGE_RE.match(value)
    if not match:
        return None
    try:
        bound = float(match.group(index + 1))
    except ValueError:
        return None
    if bound != bound:  # nan
        return None
    return bound

def _sqlite_lower(value):
    bound = _range_bound(value, 0)
    if bound is not None:
        return bound
    return value.lower() if isinstance(value, str) else value

def _sqlite_upper(value):
    bound = _range_bound(value, 1)
    if bound is not None:
        return bound
    return value.upper() if isinstance(value, str) else value

@lru_cache(maxsize=1)
def get_engine():
    '''Singleton SQLAlchemy engine for the bundled SQLite database.
    Creating an engine is comparatively expensive, so every caller shares
    this one. The database is opened read-only.'''
    if not os.path.isfile(DB_PATH):
        raise FileNotFoundError(
            'Bundled database not found at {}. '
            'Make sure you cloned the full liiondb repository.'.format(DB_PATH))
    dfndb = create_engine('sqlite:///file:{}?mode=ro&uri=true'.format(DB_PATH))

    # Postgres queries in the docs use lower(data.temp_range)/upper(...) to get
    # numrange bounds. Override SQLite's lower()/upper() so those queries work
    # unchanged: range-formatted text returns its numeric bound, everything
    # else gets normal case conversion.
    @event.listens_for(dfndb, 'connect')
    def _register_range_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function('lower', 1, _sqlite_lower)
        dbapi_connection.create_function('upper', 1, _sqlite_upper)

    return dfndb

def liiondb():
    dfndb = get_engine()
    db_connection = {'address': DB_PATH, 'dbname': 'dfndb', 'dbobject': dfndb}
    return dfndb, db_connection

def read_sql(query, engine=None):
    '''Drop-in pd.read_sql(query, engine) replacement that works on every
    pandas/SQLAlchemy version combination. pandas < 2.0 cannot execute
    plain-string queries against SQLAlchemy 2.x engines; this wraps the
    query in text() and builds the DataFrame directly.
    (Thanks to @UC0403 in github issue #23 for the diagnosis.)'''
    import pandas as pd
    from sqlalchemy import text
    if engine is None:
        engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=list(result.keys()))

def parse_range(value, default=(None, None)):
    '''Parse an exported numrange string like '[250.0, 333.0]' into a
    (lo, hi) float tuple. Missing/nan bounds fall back to `default`.'''
    lo = _range_bound(value, 0)
    hi = _range_bound(value, 1)
    return (default[0] if lo is None else lo,
            default[1] if hi is None else hi)

@lru_cache(maxsize=512)
def _compile_function(source_bytes):
    '''Compile a parameter-function source blob (bytes of a Python module
    defining `function(...)`) and return the callable. Cached so each
    function is compiled at most once per process — no disk writes, no
    importlib round-trips.'''
    namespace = {}
    exec(source_bytes.decode('utf-8'), namespace)
    return namespace['function']

def evaluate_function(function_blob, x, T=None):
    '''Evaluate a stored parameter function on input array x (and optional
    temperature T). Handles both function(x) and function(x, T) signatures.'''
    fn = _compile_function(bytes(function_blob))
    if T is not None:
        try:
            return fn(x, T)
        except TypeError:
            pass
    return fn(x)

def function_source(function_blob):
    '''Return the stored parameter function as Python source text.'''
    return bytes(function_blob).decode('utf-8').strip('\n')

def liiondb_postgres():
    '''Legacy connection to the retired Azure PostgreSQL server.
    Kept for reference only — the server is no longer online.'''
    db_connection = {
    'address' : 'dfn-parameters.postgres.database.azure.com',
    'port' : '5432',
    'username' : 'liiondb@dfn-parameters',
    'password' : 'Multi-Scale Modelling Project',
    'dbname' : 'dfndb'}
    db_connection = sqlalchemy_connect(db_connection) #Make connection
    dfndb = db_connection['dbobject']
    return dfndb, db_connection

def sqlalchemy_connect(db_connection):
    postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'
       .format(username=db_connection['username'],
               password=db_connection['password'],
               ipaddress=db_connection['address'],
               port=db_connection['port'],
               dbname=db_connection['dbname']))
    dfndb = create_engine(postgres_str)
    db_connection['dbobject']=dfndb
    return db_connection

def write_file(function_binary,write_file_path):
    with open(write_file_path, 'wb') as f:
        f.write(function_binary)

def read_data(df):
    import numpy as np
    import os
    raw_data = df['raw_data'][0]
    raw_data_class = df['raw_data_class'][0]
    function_binary = df['function'][0]
    # anchor to this module's location so the write works regardless of cwd
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    write_file_path = os.path.join(repo_root, 'streamlit_gui', 'elements', 'parameter_from_db.py')
    # write_file_path = '/tmp/parameter_from_db.py'
    # st.write(write_file_path)
    if raw_data_class == 'value':

#         print('raw_data is value')
        raw_data = df['raw_data'][0]

    elif raw_data_class == 'function':

        raw_data = np.nan
#         print('raw_data is function')
        if type(function_binary) != type(None):
            write_file(function_binary,write_file_path)
#             print('parameter_from_db.py downloaded')

    elif raw_data_class == 'array':
#         print('raw_data is array')
        csv_array = raw_data
        csv_array = csv_array.replace("{", "[")
        csv_array = csv_array.replace("}", "]")
        csv_list = eval(csv_array)
        raw_data = csv_list
        raw_data = np.array(raw_data)

    return raw_data


def gui_read_data(df):
    import numpy as np
    import os
    raw_data = df['raw_data'][0]
    raw_data_class = df['raw_data_class'][0]
    function_binary = df['function'][0]
    write_file_path = '/tmp/parameter_from_db.py'
    if raw_data_class == 'value':
        raw_data = df['raw_data'][0]
    elif raw_data_class == 'function':
        raw_data = np.nan
        if type(function_binary) != type(None):
            write_file(function_binary,write_file_path)
            write_file(''.encode(),'/tmp/__init__.py')
    elif raw_data_class == 'array':
        csv_array = raw_data
        csv_array = csv_array.replace("{", "[")
        csv_array = csv_array.replace("}", "]")
        csv_list = eval(csv_array)
        raw_data = csv_list
        raw_data = np.array(raw_data)
    return raw_data
