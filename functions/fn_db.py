import psycopg2
from sqlalchemy import create_engine
def test():
    print('hello')


def liiondb():
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
    cwd = os.getcwd()
    write_file_path = cwd + '/streamlit_gui/elements/parameter_from_db.py'
    # write_file_path = '/tmp/parameter_from_db.py'
    # st.write(write_file_path)
    if raw_data_class == 'value':

#         print('raw_data is value')
        raw_data = df['raw_data'][0]

    elif raw_data_class == 'function':

        raw_data = np.NaN
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
