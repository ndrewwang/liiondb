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
def write(session_state):

    dfndb, db_connection = fn_db.liiondb()

    st.markdown('<h5>Build SQL Query</h5>', unsafe_allow_html=True)
    form = st.form(key='Query',clear_on_submit=False)
    QUERY = form.text_area('Note: Selecting "data.data_id" is required to view parameters',height=300)
    submit = form.form_submit_button(label='Run Advanced',on_click = increment_counter)
    append_current_count()

    st.write("---")
    st.markdown('<h5>Results Table:</h5>', unsafe_allow_html=True)

    if check_refresh()==False:
        st.write(st.session_state.df_display,height = 1200)
        try:
            df_result = get_df_result(st.session_state.df_display)
        except:
            st.caption('data.data_id not selected in query')
            df_result=[]
    else:
        # try:
        df = pd.read_sql(QUERY,dfndb)
        df_display = convert_df_numrange(df)
        st.session_state.df_display = df_display
        if submit:
            st.write(df_display,height = 1200)
            st.session_state.df_display = df_display
        try:
            df_result = get_df_result(df_display)
        except:
            st.caption('data.data_id not selected in query')
            df_result=[]
        # except:
            # st.caption('Invalid SQL statement submitted')
            # df_result=[]

    session_state = st.session_state
    st.session_state.df_result = df_result
    return df_result,session_state

@st.cache
def get_df_result(df_display):
    dfndb, db_connection = fn_db.liiondb()
    data_ids = df_display['data_id']
    selection = tuple(data_ids)
    QUERY = f'''SELECT DISTINCT data.data_id, parameter.name as parameter, material.name as material, paper.paper_tag as paper,paper.url,data.raw_data, parameter.units_output, data.temp_range, data.notes
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE data.data_id IN {selection}'''
    df = pd.read_sql(QUERY,dfndb)
    df_result = convert_df_numrange(df)
    return df_result

def check_refresh():
    refresh = False
    if len(st.session_state.count_array)>1:
        if st.session_state.count_array[-2]!=st.session_state.count_array[-1]:
            refresh = True
    return refresh

def increment_counter():
    st.session_state.count +=1

def append_current_count():
    st.session_state.count_array.append(st.session_state.count)
# @st.cache
def convert_df_numrange(df):
    import numpy as np
    if 'temp_range' in df.keys():
        A = df.temp_range.astype(str)
        df.temp_range = A
    if 'input_range' in df.keys():
        A = df.input_range.astype(str)
        df.input_range = A
    return df
