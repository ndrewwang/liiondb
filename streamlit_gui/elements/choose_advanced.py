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
import streamlit_gui.elements.single_parameter


# DASHBOARD PAGE ====================

def write(df_result,session_state):
    st.session_state=session_state
    selections = []
    dfndb, db_connection = fn_db.liiondb()
    id = df_result['data_id'].map(str)
    param = df_result['parameter']
    mat = df_result['material']
    tag = df_result['paper'].tolist()
    space = ["   |   "] * len(tag)
    A = id + param + mat
    data_list = id + space + param + space + mat + space + tag
    form = st.form(key='my_form')
    selections = form.multiselect('Choose a single parameter to see full details or multiple to run a comparison',data_list)
    submit_button = form.form_submit_button(label='Go', on_click = append_current_count)
    if 'count' not in st.session_state:
        st.session_state.count = 0
    return selections, submit_button, session_state


def increment_counter():
    st.session_state.count +=1

def append_current_count():
    st.session_state.count_array.append(st.session_state.count)

        #MULTISELECT ROWS, IF THEY ARE THE SAME METHOD, THEN PLOT THEM TOGETHER
