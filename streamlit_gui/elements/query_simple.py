import streamlit as st
import psycopg2
import inspect
import sys
import os
import importlib
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import pandas as pd
import numpy as np
import webbrowser
import markdown
import base64

# DASHBOARD PAGE ====================
# @st.cache(suppress_st_warning=True)
def write():
    df_result = []
    dfndb, db_connection = fn_db.liiondb()
    st.markdown('<h5>Query Builder:</h5>', unsafe_allow_html=True)
    col1,col2,col3 = st.columns(3)

    #COLUMN1
    df0 = load_all_table_joins(0)
    selection0 = col1.multiselect('1. Type',df0)
    selection0 = single_or_multi(selection0)

    #COLUMN2
    df1 = load_all_table_joins(1)
    selectlist = df1[pd.DataFrame(df1['class'].tolist()).isin(selection0).any(axis=1).values]
    selectlist = selectlist.sort_values('parameter_id')
    selection1 = col2.multiselect('2. Parameter',selectlist['name'].drop_duplicates())
    selection1 = single_or_multi(selection1)

    #COLUMN3
    df2 = load_all_table_joins(2)
    df2 = df2[pd.DataFrame(df2['class'].tolist()).isin(selection0).any(axis=1).values]
    selectlist = df2[pd.DataFrame(df2['parameter_name'].tolist()).isin(selection1).any(axis=1).values]
    selectlist = selectlist.sort_values('material_name')
    selectlist = selectlist['material_name']
    selection2 = col3.multiselect('3. Material',selectlist.drop_duplicates())
    selection2 = single_or_multi(selection2)


    st.markdown('<h5>Results Table:</h5>', unsafe_allow_html=True)

    if min([len(selection0),len(selection1),len(selection2)]) < 2:
        st.caption('Not enough options selected')
    else:
        QUERY = f'''SELECT DISTINCT data.data_id, parameter.name as parameter, material.name as material, paper.paper_tag as paper,paper.url,data.raw_data, parameter.units_output, data.temp_range, data.notes
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE material.class IN {selection0}
        AND parameter.name IN {selection1}
        AND material.name IN {selection2}'''
        df = pd.read_sql(QUERY,dfndb)
        df = convert_df_numrange(df)
        df_result = df.sort_values('data_id')
        st.write(df_result,height = 1200)
    return df_result

@st.cache
def load_all_table_joins(i):
    dfndb, db_connection = fn_db.liiondb()
    # list 1: all material types
    QUERY0 = '''
            SELECT DISTINCT material.class
            FROM material
            '''

    QUERY1 = '''
            SELECT parameter.parameter_id, parameter.name, material.class
            FROM parameter
            JOIN data on data.parameter_id = parameter.parameter_id
            JOIN material on material.material_id = data.material_id
            '''

    QUERY2 = '''
        SELECT material.name as material_name, parameter.name as parameter_name, material.class
        FROM parameter
        JOIN data on data.parameter_id = parameter.parameter_id
        JOIN material on material.material_id = data.material_id
        '''
    QUERY = [QUERY0,QUERY1,QUERY2]
    df_selections = pd.read_sql(QUERY[i],dfndb)
    return df_selections

def single_or_multi(selections):
    tupe_select = tuple(selections)+tuple(['$$$$'])
    return tupe_select

def convert_df_numrange(df):
    import ast
    import numpy as np
    if 'temp_range' in df.keys():
        A = df.temp_range.astype(str)
        df.temp_range = A
    if 'input_range' in df.keys():
        A = df.input_range.astype(str)
        df.input_range = A
    return df
