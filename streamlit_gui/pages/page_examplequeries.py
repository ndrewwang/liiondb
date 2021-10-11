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
import streamlit_gui.elements.example_advanced_queries
# DASHBOARD PAGE ====================
def write():
    st.title(":outbox_tray: Example Advanced Queries")
    st.write('---')

    samplesdict=streamlit_gui.elements.example_advanced_queries.write()
    the_example = st.selectbox('Choose some example queries from this drop down list to get started!',list(samplesdict.keys()))
    query_prefill = samplesdict[the_example]
    st.text_area('Copy and paste over to "Advanced Queries" tab to see results',query_prefill,height = 300)
