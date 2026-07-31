import streamlit as st
import pandas as pd
import streamlit_gui.queries as queries

# ADVANCED SQL QUERY BOX ====================

def write():
    st.markdown('<h5>Build SQL Query</h5>', unsafe_allow_html=True)
    with st.form(key='Query', clear_on_submit=False):
        QUERY = st.text_area('Note: Selecting "data.data_id" is required to view parameters',
                             st.session_state.get('advanced_sql', ''), height=300)
        submit = st.form_submit_button(label='Run Advanced')
    if submit and QUERY.strip():
        st.session_state.advanced_sql = QUERY

    st.write('---')
    st.markdown('<h5>Results Table:</h5>', unsafe_allow_html=True)

    sql = st.session_state.get('advanced_sql', '').strip()
    df_result = []
    if not sql:
        st.caption('Enter a SQL query above and press Run')
        return df_result

    try:
        df_display = queries.run_query(sql)
    except Exception as e:
        st.error('Invalid SQL statement: %s' % e)
        return df_result

    st.dataframe(df_display, height=400, hide_index=True)
    if 'data_id' not in df_display.columns:
        st.caption('data.data_id not selected in query')
    elif len(df_display) == 0:
        st.caption('Query returned no rows')
    else:
        try:
            data_ids = tuple(int(i) for i in df_display['data_id'].dropna())
        except (ValueError, TypeError):
            st.error('The data_id column must contain integer data.data_id values')
            return df_result
        df_result = get_df_result(data_ids)
    return df_result


@st.cache_data(show_spinner=False)
def get_df_result(data_ids):
    '''Standard results-table columns for the data_ids a user query returned.'''
    id_list = '(' + ', '.join(str(i) for i in data_ids) + ')'
    QUERY = f'''SELECT DISTINCT data.data_id, parameter.name as parameter, material.name as material, paper.paper_tag as paper, paper.url, data.raw_data, parameter.units_output, data.temp_range, data.notes
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE data.data_id IN {id_list}'''
    return queries.run_query(QUERY)
