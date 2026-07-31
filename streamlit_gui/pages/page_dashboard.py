import streamlit as st
import streamlit_gui.elements.query_simple
import streamlit_gui.elements.choose_parameters
import streamlit_gui.elements.single_parameter
import streamlit_gui.elements.multiparameter_comparison

# DASHBOARD PAGE ====================

def write():
    st.title(":mag_right: Parameter Dashboard")
    st.write("---")
    df_result = streamlit_gui.elements.query_simple.write()
    st.write("---")

    if len(df_result) == 0:
        return
    st.markdown('<h5>Select parameters to display:</h5>', unsafe_allow_html=True)
    selections = streamlit_gui.elements.choose_parameters.write(df_result)

    if len(selections) == 1:
        streamlit_gui.elements.single_parameter.write(selections)
    elif len(selections) > 1:
        streamlit_gui.elements.multiparameter_comparison.write(selections)
