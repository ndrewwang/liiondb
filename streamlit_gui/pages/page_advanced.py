import streamlit as st
import streamlit_gui.elements.query_box
import streamlit_gui.elements.choose_advanced
import streamlit_gui.elements.single_parameter
import streamlit_gui.elements.multiparameter_comparison

# ADVANCED QUERIES PAGE ====================

def write():
    st.title(":rocket: Advanced Queries")
    st.write("---")
    df_result = streamlit_gui.elements.query_box.write()
    st.write("---")

    if len(df_result) == 0:
        return
    st.markdown('<h5>Select data_id to display:</h5>', unsafe_allow_html=True)
    selections = streamlit_gui.elements.choose_advanced.write(df_result)

    if len(selections) == 1:
        streamlit_gui.elements.single_parameter.write(selections)
    elif len(selections) > 1:
        streamlit_gui.elements.multiparameter_comparison.write(selections)
