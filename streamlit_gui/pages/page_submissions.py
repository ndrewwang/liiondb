import streamlit as st

# CONTRIBUTE PAGE ====================

def write():
    st.title(":postbox: Contribute")
    st.write('---')

    st.markdown('<h5> To offer site feedback or contribute new datasets, please get in touch via:</h5>',
                unsafe_allow_html=True)

    st.markdown('* The `#param-database` channel on the [**PyBaMM slack space**](https://pybamm.slack.com), '
                '([how to join](https://www.pybamm.org/contact))')
    st.markdown('* The LiionDB GitHub [page](https://github.com/ndrewwang/liiondb)')
