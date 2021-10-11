import streamlit as st
import webbrowser

# DASHBOARD PAGE ====================
def write():
    st.title(":information_source: More about LiionDB")
    st.write('---')

    st.markdown('<h5>Read the LiionDB parameterisation review preprint:</h5>', unsafe_allow_html=True)
    if st.button('Archive Link'):
        webbrowser.open_new_tab('https://www.doi.org')

    st.write('---')
    st.markdown('<h5>GitHub:</h5>', unsafe_allow_html=True)
    if st.button('LiionDB on GitHub'):
        webbrowser.open_new_tab('https://github.com/ndrewwang/liiondb')

    st.write('---')
    st.markdown('<h5>LiionDB entity relationship diagram:</h5>', unsafe_allow_html=True)
    # st.write('')

    st.image('/Users/andrew/Dropbox/Research/DPhil/0 dfndb/liiondb_working/streamlit_gui/media/liiondb_erd.png')
