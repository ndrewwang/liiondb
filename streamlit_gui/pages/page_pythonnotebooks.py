import streamlit as st
# DASHBOARD PAGE ====================
def write():
    st.title(":snake: Using LiionDB with Python Notebooks")
    st.write('---')

    st.write('If you would like to interact with the parameter database with programmatically, check out these Google Colab python notebooks here:')

    st.markdown('1. [Example LiionDB queries](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/1_Example_Queries.ipynb)')
    st.markdown('2. [Plotting parameter comparisons](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/2_Parameter_Plotter.ipynb)')
