import streamlit as st
# DASHBOARD PAGE ====================
def write():
    st.title(":snake: Access LiionDB with Python Notebooks")
    st.write('---')

    st.write('LiionDB is a PostgreSQL parameter database that can be interacted with programmatically, we provide examples through Google Colab python notebooks here:')

    st.markdown('1. [Example LiionDB queries](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/1_Example_Queries.ipynb)')
    st.markdown('2. [Plotting parameter comparisons](https://colab.research.google.com/github/ndrewwang/liiondb/blob/main/python%20notebooks/2_Parameter_Plotter.ipynb)')
