import streamlit as st
import streamlit_gui.elements.example_advanced_queries

# EXAMPLE QUERIES PAGE ====================

def write():
    st.title(":outbox_tray: Example Advanced Queries")
    st.write('---')

    samplesdict = streamlit_gui.elements.example_advanced_queries.write()
    the_example = st.selectbox('Choose some example queries from this drop down list to get started!',
                               list(samplesdict.keys()))
    query_prefill = samplesdict[the_example]
    st.code(query_prefill.strip(), language='sql')
    st.caption('Copy and paste over to the "Advanced Queries" page to see results')
