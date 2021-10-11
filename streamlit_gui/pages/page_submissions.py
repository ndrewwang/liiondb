import streamlit as st
# DASHBOARD PAGE ====================
def write():
    st.title(":postbox: Contribute")
    st.write('---')

    st.markdown('<h5> To offer site feedback or contribute new datasets, please get in touch via:</h5>', unsafe_allow_html=True)

    st.markdown('* The `#param-database` channel on the [**PyBaMM slack space**](http://www.google.com/url?q=http%3A%2F%2Fpybamm.slack.com&sa=D&sntz=1&usg=AFQjCNEwLDGWiQ_8ospl4Rjx7UccT2GW1g), ([how to join](https://www.pybamm.org/contact))')
    st.markdown('* The LiionDB GitHub [page](https://github.com/ndrewwang/liiondb)')
