import streamlit as st
import pandas as pd
import numpy as np
import functions.fn_db as fn_db

# Single choke-point for all GUI database access. Every query result is
# cached by its SQL text (st.cache_data), and all queries share one
# SQLAlchemy engine (fn_db.get_engine is an lru_cache singleton), so a
# widget interaction only ever re-runs SQL it has never seen before.


@st.cache_data(show_spinner=False)
def run_query(sql):
    dfndb, _ = fn_db.liiondb()
    df = pd.read_sql(sql, dfndb)
    return stringify_ranges(dedupe_columns(df))


def dedupe_columns(df):
    '''Suffix repeated column names (SELECT a.name, b.name -> name, name_2)
    so streamlit's dataframe renderer doesn't reject the result.'''
    seen = {}
    cols = []
    for col in df.columns:
        seen[col] = seen.get(col, 0) + 1
        cols.append(col if seen[col] == 1 else '%s_%d' % (col, seen[col]))
    df.columns = cols
    return df


def stringify_ranges(df):
    for col in ('temp_range', 'input_range'):
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


DISPLAY_QUERY = '''
    SELECT DISTINCT data.data_id,
           data.raw_data_class,
           data.temp_range as temp_range,
           parameter.name as param_name,
           parameter.symbol as param_symbol,
           parameter.units_output as unit_out,
           parameter.units_input as unit_in,
           paper.paper_tag,
           paper.url,
           paper.title,
           paper.authors,
           data.raw_data,
           data.notes,
           {method_cols}
           material.name as mat_name,
           material.class as mat_class,
           material.note as mat_note
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    {method_joins}
    WHERE data.data_id = {data_id}
'''


@st.cache_data(show_spinner=False)
def query_to_display(data_id):
    '''Full display record for one data_id (with methods when available).'''
    data_id = int(data_id)
    with_method = DISPLAY_QUERY.format(
        method_cols='method.name as method_name, method.description as method_desc,',
        method_joins='JOIN data_method ON data.data_id = data_method.data_id '
                     'JOIN method ON data_method.method_id = method.method_id',
        data_id=data_id)
    dispdf = run_query(with_method)
    if dispdf.size == 0:
        no_method = DISPLAY_QUERY.format(method_cols='', method_joins='', data_id=data_id)
        dispdf = run_query(no_method)
    return dispdf


@st.cache_data(show_spinner=False)
def data_row(data_id):
    '''Raw data table row for one data_id (raw_data, function blob, ranges).'''
    dfndb, _ = fn_db.liiondb()
    df = pd.read_sql(f'SELECT * FROM data WHERE data_id = {int(data_id)}', dfndb)
    return stringify_ranges(df)


@st.cache_data(show_spinner=False)
def parse_array(raw_data):
    '''Parse a Postgres-style array literal {{x1,y1},{x2,y2},...} into a
    numpy array of shape (n, 2).'''
    csv_array = raw_data.replace('{', '[').replace('}', ']')
    return np.array(eval(csv_array))


@st.cache_data(show_spinner=False)
def evaluate_function_curve(data_id, T, n_points=500):
    '''Evaluate the stored parameter function for one data_id over its
    input range at temperature T. Cached by (data_id, T) so scrubbing the
    temperature slider back and forth is free.'''
    df = data_row(data_id)
    c_low, c_max = fn_db.parse_range(df.input_range.iloc[0], default=(0.0, 1.0))
    c_low, c_max = c_low + 0.001, c_max - 0.001
    x = np.linspace(c_low, c_max, n_points)
    y = fn_db.evaluate_function(df['function'].iloc[0], x, T)
    y = np.broadcast_to(np.asarray(y, dtype=float), x.shape).copy()
    return x, y


def format_options(df_result):
    '''Build the "id  |  parameter  |  material  |  paper" option strings
    used by the selection multiselects.'''
    sep = '  |  '
    return (df_result['data_id'].map(str) + sep
            + df_result['parameter'] + sep
            + df_result['material'] + sep
            + df_result['paper']).tolist()


def parse_option(option):
    '''Inverse of format_options for one option string.'''
    parts = [p.strip() for p in option.split('|')]
    return {'data_id': int(parts[0]),
            'parameter': parts[1] if len(parts) > 1 else '',
            'material': parts[2] if len(parts) > 2 else '',
            'paper': parts[3] if len(parts) > 3 else ''}
