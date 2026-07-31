import streamlit as st
import streamlit_gui.queries as queries

# PARAMETER SELECTION ====================

def write(df_result):
    data_list = queries.format_options(df_result)
    selections = st.multiselect(
        'Choose a single parameter to see full details, or multiple to plot a comparison',
        data_list)
    return selections
