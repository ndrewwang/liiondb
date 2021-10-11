import streamlit as st
import webbrowser

# DASHBOARD PAGE ====================
def write():
    st.title(":information_source: More about LiionDB")
    st.write('---')

    st.markdown('<h5>Read the LiionDB parameterisation review preprint:</h5>', unsafe_allow_html=True)
    link = '[**Prepint Link**](https://www.doi.org)'
    st.markdown(link, unsafe_allow_html=True)

    st.write('---')
    st.markdown('<h5>GitHub:</h5>', unsafe_allow_html=True)
    link = '[**PLiionDB on GitHub**](https://github.com/ndrewwang/liiondb)'
    st.markdown(link, unsafe_allow_html=True)

    st.write('---')
    st.markdown('<h5>LiionDB entity relationship diagram:</h5>', unsafe_allow_html=True)
    # st.write('')

    st.image('streamlit_gui/media/liiondb_erd.png')
