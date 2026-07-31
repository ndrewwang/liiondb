import streamlit as st

# PAPER INFORMATION ====================

def write(dispdf):
    st.write('---')
    st.markdown('***PAPER***')
    st.markdown('<h3>' + str(dispdf.title.iloc[0]) + '</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.markdown(str(dispdf.authors.iloc[0]))
    url = dispdf.url.iloc[0]
    if url:
        col2.markdown('[**Paper URL**](%s)' % url)

    col1, col2, col3 = st.columns(3)
    col1.markdown('***NOTES***')
    col1.write(dispdf.notes.iloc[0])
    col2.markdown('***TEMP RANGE*** [K]')
    col2.write(dispdf.temp_range.iloc[0])
    col3.markdown('***METHODS***')
    if 'method_name' in dispdf.columns:
        methods = dispdf.method_name.dropna().drop_duplicates()
        col3.write(', '.join(methods) if len(methods) else 'No method available')
    else:
        col3.write('No method available')
