import streamlit as st
import pandas as pd
import streamlit_gui.queries as queries
import streamlit_gui.elements.paper_info
import streamlit_gui.elements.plot_single_parameter

# SINGLE PARAMETER DETAIL ====================

def write(selections):
    data_id = queries.parse_option(selections[0])['data_id']
    dispdf = queries.query_to_display(data_id)
    if dispdf.size == 0:
        st.caption('No data found for data_id %s' % data_id)
        return

    st.markdown('***PARAMETER***')
    col1, col2 = st.columns(2)
    col1.title(dispdf.param_symbol.iloc[0])
    col2.markdown('<h2>' + dispdf.mat_class.iloc[0].title() + ' ' + dispdf.param_name.iloc[0] + '</h2>',
                  unsafe_allow_html=True)

    st.markdown('***MATERIAL***')
    col1, col2 = st.columns(2)
    col1.write(dispdf.mat_name.iloc[0])
    col2.write(dispdf.mat_note.iloc[0])

    df = queries.data_row(data_id)
    streamlit_gui.elements.plot_single_parameter.write(dispdf, df)
    streamlit_gui.elements.paper_info.write(dispdf)
