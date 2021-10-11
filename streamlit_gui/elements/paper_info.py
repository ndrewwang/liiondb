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

def write(dispdf):
        #PAPER INFORMATION
    st.write('---')
    st.markdown('***PAPER***')
    st.markdown('<h3>'+dispdf.title.iloc[0]+'</h3>',unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.markdown(dispdf.authors.iloc[0])
    col2.markdown("[**Open Paper URL**]({dispdf.url.iloc[0]})")
    # if col2.button('Open paper URL'):
        # webbrowser.open_new_tab(dispdf.url.iloc[0])
    #NOTES TEMPRANGE, & METHOD
    col1, col2, col3 = st.columns(3)
    col1.markdown('***NOTES***')
    col1.write(dispdf.notes.iloc[0])
    col2.markdown('***TEMP RANGE*** [K]')
    col2.write(dispdf.temp_range.iloc[0])
    col3.markdown('***METHODS***')
    try:
        methoddf = dispdf.method_name
        methoddf = methoddf.astype(str) + ','
        col3.write(methoddf.to_string(index=False))
    except:
        col3.write('No method available')
        # st.write(dispdf)

if __name__ == "__main__":
    write()
