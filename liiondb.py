import streamlit as st
import psycopg2
import inspect
import sys
import os
import awesome_streamlit as ast
import importlib
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import pandas as pd
import numpy as np
import webbrowser
import markdown
import base64
import streamlit_gui.pages.page_dashboard
import streamlit_gui.pages.page_advanced
import streamlit_gui.pages.page_examplequeries
import streamlit_gui.pages.page_moreinfo
import streamlit_gui.pages.page_submissions
import streamlit_gui.pages.page_pythonnotebooks
import streamlit_gui.pages.page_testplot

def main():
    # ================ SIDE BAR PAGES AND TEXT ===============================
    PAGES = {
            "Parameter Dashboard":[],
            "Advanced Queries": [],
            "Example Advanced Queries": [],
            "Python Notebooks": [],
            "Contribute": [],
            "More Info": [],
    }
    st.sidebar.title(":battery: LiionDB")

    st.sidebar.markdown('<h2>DFN Parameter Database</h2>', unsafe_allow_html=True)

    selection = st.sidebar.radio("Select page", tuple(PAGES.keys()))

    page = PAGES[selection]

    st.sidebar.markdown('<h3>About</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "This interactive database of DFN-type battery model parameters "
        "accompanies the review manuscript: "
        "[**Parameterising Continuum-Level Li-ion Battery Models**.](https://www.overleaf.com/project/5ed63d9378cbf700018a2018)"
        " If you use LiionDB in your work, please cite our paper at: "
        "[doi.org](https://www.doi.org/)")

    st.sidebar.markdown('<h3>Support</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "LiionDB is supported by the "
        "[**Multi-Scale Modelling**](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/)"
        " project through "
        "[**The Faraday Institution**.](https://www.faraday.ac.uk/)")
    # st.sidebar.image('streamlit_gui/media/msm.png',width=50,output_format='PNG')

    PAGES = {
            "Parameter Dashboard": streamlit_gui.pages.page_dashboard,
            "Advanced Queries": streamlit_gui.pages.page_advanced,
            "Example Advanced Queries": streamlit_gui.pages.page_examplequeries,
            "Python Notebooks": streamlit_gui.pages.page_pythonnotebooks,
            "Contribute": streamlit_gui.pages.page_submissions,
            "More Info": streamlit_gui.pages.page_moreinfo,
    }
    page = PAGES[selection]
    ast.shared.components.write_page(page)

if __name__ == "__main__":
    # st.set_page_config(layout="wide")
    main()
