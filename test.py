import streamlit as st
import pandas as pd


data = pd.DataFrame([[pd.Timestamp("2021-01-01"),pd.Timestamp("2021-01-02")], ["abc", "def"]],
       columns = ["testcol1", "testcol2"])
st.dataframe(data)
