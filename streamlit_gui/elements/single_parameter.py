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
import altair as alt
import markdown
import base64

import streamlit_gui.elements.paper_info
import streamlit_gui.elements.plot_single_parameter

def write(selections,session_state):
    selections = [int(i.split(' |')[0]) for i in selections]
    st.session_state = session_state
    dfndb, db_connection = fn_db.liiondb()
    try:
        data_id = selections[0]
        if isinstance(st.session_state.dispdf, pd.DataFrame) == False:
            st.session_state.dispdf = query_to_display(data_id)
        if check_refresh():
            st.session_state.dispdf = query_to_display(data_id)

        dispdf = st.session_state.dispdf
        st.markdown('***PARAMETER***')
        col1, col2 = st.columns(2)
        col1.title(dispdf.param_symbol.iloc[0])
        col2.markdown('<h2>' + dispdf.mat_class.iloc[0].title() + ' '+ dispdf.param_name.iloc[0]+ '</h2>',unsafe_allow_html=True)
        #MATERIAL
        st.markdown('***MATERIAL***')
        col1, col2 = st.columns(2)
        col1.write(dispdf.mat_name.iloc[0])
        col2.write(dispdf.mat_note.iloc[0],unsafe_allow_html=True)

        df = perform_data_query(data_id)
        session_state = st.session_state
        session_state = streamlit_gui.elements.plot_single_parameter.write(dispdf,df,session_state)
        streamlit_gui.elements.paper_info.write(dispdf)

    except IndexError:
        session_state = st.session_state


    return session_state

@st.cache
def perform_data_query(data_id):
    dfndb, db_connection = fn_db.liiondb()
    QUERY = f'SELECT * FROM data WHERE data_id = {data_id}'
    df = pd.read_sql(QUERY,dfndb)
    return df
#
def check_refresh():
    refresh = False
    if len(st.session_state.count_array)>1:
        if st.session_state.count_array[-2]!=st.session_state.count_array[-1]:
            refresh = True
    return refresh


@st.cache
def query_to_display(data_id):
     dfndb, db_connection = fn_db.liiondb()

     QUERY = f'''
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
              method.name as method_name,
              method.description as method_desc,
              material.name as mat_name,
              material.class as mat_class,
              material.note as mat_note
             FROM data
             JOIN paper ON paper.paper_id = data.paper_id
             JOIN material ON material.material_id = data.material_id
             JOIN parameter ON parameter.parameter_id = data.parameter_id
             JOIN data_method ON data.data_id = data_method.data_id
             JOIN method ON data_method.method_id = method.method_id
             WHERE data.data_id = {data_id}
             '''
     QUERY_nomethod = f'''
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
              material.name as mat_name,
              material.class as mat_class,
              material.note as mat_note
             FROM data
             JOIN paper ON paper.paper_id = data.paper_id
             JOIN material ON material.material_id = data.material_id
             JOIN parameter ON parameter.parameter_id = data.parameter_id
             WHERE data.data_id = {data_id}
             '''
     dispdf = pd.read_sql(QUERY,dfndb)
     if dispdf.size == 0:
         dispdf = pd.read_sql(QUERY_nomethod,dfndb)
     dispdf = convert_df_numrange(dispdf)
     return dispdf

@st.cache
def convert_df_numrange(df):
 import ast
 import numpy as np
 if 'temp_range' in df.keys():
     A = df.temp_range.astype(str) #convert to string
     df.temp_range = A
 elif 'input_range' in df.keys():
     A = df.input_range.astype(str) #convert to string
     df.input_range = A
 return df

if __name__ == "__main__":
    write()
