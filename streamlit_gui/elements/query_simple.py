import streamlit as st
import pandas as pd
import streamlit_gui.queries as queries

# QUERY BUILDER ====================

def write():
    df_result = []
    st.markdown('<h5>Query Builder:</h5>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    # COLUMN 1 — material class
    df0 = queries.run_query('SELECT DISTINCT material.class FROM material')
    selection0 = col1.multiselect('1. Type', sorted(df0['class'].dropna()))

    # COLUMN 2 — parameters available for those classes
    df1 = queries.run_query('''
        SELECT DISTINCT parameter.parameter_id, parameter.name, material.class
        FROM parameter
        JOIN data on data.parameter_id = parameter.parameter_id
        JOIN material on material.material_id = data.material_id
        ''')
    selectlist = df1[df1['class'].isin(selection0)].sort_values('parameter_id')
    selection1 = col2.multiselect('2. Parameter', selectlist['name'].drop_duplicates())

    # COLUMN 3 — materials with data for those parameters
    df2 = queries.run_query('''
        SELECT DISTINCT material.name as material_name, parameter.name as parameter_name, material.class
        FROM parameter
        JOIN data on data.parameter_id = parameter.parameter_id
        JOIN material on material.material_id = data.material_id
        ''')
    df2 = df2[df2['class'].isin(selection0)]
    selectlist = df2[df2['parameter_name'].isin(selection1)].sort_values('material_name')
    selection2 = col3.multiselect('3. Material', selectlist['material_name'].drop_duplicates())

    st.markdown('<h5>Results Table:</h5>', unsafe_allow_html=True)

    if min([len(selection0), len(selection1), len(selection2)]) < 1:
        st.caption('Not enough options selected')
    else:
        QUERY = f'''SELECT DISTINCT data.data_id, parameter.name as parameter, material.name as material, paper.paper_tag as paper, paper.url, data.raw_data, parameter.units_output, data.temp_range, data.notes
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE material.class IN {sql_tuple(selection0)}
        AND parameter.name IN {sql_tuple(selection1)}
        AND material.name IN {sql_tuple(selection2)}'''
        df = queries.run_query(QUERY)
        df_result = df.sort_values('data_id')
        st.dataframe(df_result, height=400, hide_index=True)
    return df_result


def sql_tuple(selections):
    '''Render a python list as a SQL IN-tuple, safe for single elements.'''
    quoted = ["'" + str(s).replace("'", "''") + "'" for s in selections]
    return '(' + ', '.join(quoted) + ')'
