import os
import streamlit as st

# MORE INFO PAGE ====================

MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'media')

def write():
    st.title(":information_source: More about LiionDB")
    st.write('---')

    st.markdown('<h5>Read the LiionDB parameterisation review:</h5>', unsafe_allow_html=True)
    st.markdown('[**Parameterising continuum-level Li-ion battery models** '
                '(Prog. Energy 2022)](https://doi.org/10.1088/2516-1083/ac692c)')

    st.write('---')
    st.markdown('<h5>GitHub:</h5>', unsafe_allow_html=True)
    st.markdown('[**LiionDB on GitHub**](https://github.com/ndrewwang/liiondb)')

    st.write('---')
    st.markdown('<h5>LiionDB entity relationship diagram:</h5>', unsafe_allow_html=True)
    st.image(os.path.join(MEDIA_DIR, 'liiondb_erd.png'))
