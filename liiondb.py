import streamlit as st

st.set_page_config(page_title='LiionDB', page_icon=':battery:')

import streamlit_gui.pages.page_dashboard
import streamlit_gui.pages.page_advanced
import streamlit_gui.pages.page_examplequeries
import streamlit_gui.pages.page_moreinfo
import streamlit_gui.pages.page_submissions
import streamlit_gui.pages.page_pythonnotebooks


def main():
    # ================ SIDE BAR PAGES AND TEXT ===============================
    PAGES = {
        "Parameter Dashboard": streamlit_gui.pages.page_dashboard,
        "Advanced Queries": streamlit_gui.pages.page_advanced,
        "Example Advanced Queries": streamlit_gui.pages.page_examplequeries,
        "Accessing LiionDB": streamlit_gui.pages.page_pythonnotebooks,
        "Contribute": streamlit_gui.pages.page_submissions,
        "More Info": streamlit_gui.pages.page_moreinfo,
    }
    st.sidebar.title(":battery: LiionDB")

    st.sidebar.markdown('<h2>DFN Parameter Database</h2>', unsafe_allow_html=True)

    selection = st.sidebar.radio("Select page", tuple(PAGES.keys()))

    st.sidebar.markdown('<h3>About</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "LiionDB is a database of DFN-type battery model parameters "
        "that accompanies the review manuscript: "
        "[**Parameterising Continuum-Level Li-ion Battery Models**.](https://iopscience.iop.org/article/10.1088/2516-1083/ac692c)"
        " If you use LiionDB in your work, please cite our paper at DOI: "
        "[10.1088/2516-1083/ac692c](https://iopscience.iop.org/article/10.1088/2516-1083/ac692c)")

    st.sidebar.markdown('<h3>Support</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "LiionDB is supported by the "
        "[**Multi-Scale Modelling**](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/)"
        " project through "
        "[**The Faraday Institution**.](https://www.faraday.ac.uk/)")

    page = PAGES[selection]
    page.write()


if __name__ == "__main__":
    main()
