import streamlit as st
from streamlit.hashing import _CodeHasher
import psycopg2
import inspect
import sys
import os
import importlib
from modules import fn_sql
from modules import fn_db
from modules import fn_plot
import pandas as pd
import numpy as np
import webbrowser
import altair as alt
import markdown

try:
    # Before Streamlit 0.65
    from streamlit.ReportThread import get_report_ctx
    from streamlit.server.Server import Server
except ModuleNotFoundError:
    # After Streamlit 0.65
    from streamlit.report_thread import get_report_ctx
    from streamlit.server.server import Server

def main():
    state = _get_state()
    pages = {
        "Dashboard": page_dashboard,
        "Advanced Queries": page_advanced,
    }
    st.sidebar.title(":battery: LiionDB")
    st.sidebar.markdown('<h2>DFN Parameter Database</h2>', unsafe_allow_html=True)
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))
    # Display the selected page with the session state
    pages[page](state)
    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()

def page_dashboard(state):
    st.title(":mag_right: Dashboard")
    @st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
    def init_connection():
        db_connection_string = {
        'address' : 'dfn-parameters.postgres.database.azure.com',
        'port' : '5432',
        'username' : 'testuser@dfn-parameters',
        'password' : 'testuserpassword',
        'dbname' : 'dfndb',
        }
        db_connection = fn_sql.sqlalchemy_connect(db_connection_string) #Make connection

        dfndb = db_connection['dbobject']
        return dfndb
    dfndb = init_connection()
    # display_state_values(state)
    st.write("---")
    col1,col2,col3,col4 = st.beta_columns(4)

    #MATERIAL first
    # FIRST SIDE BAR DROPDOWN


    QUERY = '''
            SELECT DISTINCT material.class
            FROM material
            '''
    df = pd.read_sql(QUERY,dfndb)
    classdf = df
    state.mat_type = col1.selectbox('1. Material Type',classdf)

    #PARAMETER SECOND
    QUERY = f'''
            SELECT DISTINCT parameter.name
            FROM parameter
            WHERE parameter.class = '{state.mat_type}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    paramdf = df
    state.param_name = col2.selectbox('2. Parameter',paramdf)

    QUERY = f'''
            SELECT DISTINCT material.name
            FROM material
            JOIN data ON data.material_id = material.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE material.class = '{state.mat_type}'
            AND parameter.name = '{state.param_name}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    matdf = df
    state.mat_name = col3.selectbox('3. Material Name',matdf)

    QUERY = f'''
            SELECT DISTINCT paper.paper_tag
            FROM paper
            JOIN data ON data.paper_id = paper.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE material.class = '{state.mat_type}'
            AND parameter.name = '{state.param_name}'
            AND material.name = '{state.mat_name}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    papdf = df
    state.paper_name = col4.selectbox('4. Paper Source',papdf)
        # state.query = form.text_area('Note: "data.data_id" required',state.query,height=300)


    st.markdown('<h3>Results Table</h3>', unsafe_allow_html=True)
    state.dashquery = f'''SELECT DISTINCT data.data_id,parameter.name as parameter, material.name as material, paper.paper_tag,data.raw_data, parameter.units_output, data.temp_range, data.notes
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE parameter.name = '{state.param_name}'
    AND material.name = '{state.mat_name}'
    AND paper.paper_tag = '{state.paper_name}'
                '''
    df = pd.read_sql(state.dashquery,dfndb)
    df_result = st.dataframe(df.head(1),height = 1000)
    # df_result = st.dataframe(df,height = 1000)
    state.data_id = df.data_id.iloc[0]
    # st.write(state.data_id)
    # form = st.form(key='expandData',clear_on_submit=False)
    # state.data_id = form.selectbox('Choose row:',options)
    # submit_button = form.form_submit_button(label='Load Data')
    # if submit_button:
    QUERY = f'''
            SELECT DISTINCT data.data_id,
            data.raw_data_class,
            data.temp_range as temp_range,
            parameter.name as param_name,
            parameter.symbol as param_symbol,
            parameter.class as param_class,
            parameter.units_output as unit_out,
            parameter.units_input as unit_in,
             paper.paper_tag,
             paper.url,
             paper.title,
             paper.authors,
             data.raw_data,
             data.notes,
             method.name as method_name,
             method.description as method_desc,
             material.name as mat_name,
             material.class as mat_class,
             material.note as mat_note
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            JOIN data_method ON data.data_id = data_method.data_id
            JOIN method ON data_method.method_id = method.method_id
            WHERE data.data_id= %s
            '''%str(state.data_id)
    dispdf = pd.read_sql(QUERY,dfndb)
    # st.dataframe(dispdf.transpose(),height = 1000)
    st.write("---")
    #PARAMETER
    st.markdown('***PARAMETER***')
    col1, col2 = st.beta_columns(2)
    # col1.latex(dispdf.param_symbol.iloc[0][1:-1])
    col1.title(dispdf.param_symbol.iloc[0])
    col2.markdown('<h2>' + dispdf.param_class.iloc[0].title() + ' '+ dispdf.param_name.iloc[0]+ '</h2>',unsafe_allow_html=True)
    #MATERIAL
    st.markdown('***MATERIAL***')
    col1, col2 = st.beta_columns(2)
    col1.write(dispdf.mat_name.iloc[0])
    col2.write(dispdf.mat_note.iloc[0],unsafe_allow_html=True)

    st.write('---')
    #PLOTTING SHOWING Data
    log = 'linear'
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]

    QUERY = 'SELECT * FROM data WHERE data_id = %s;' %str(state.data_id)
    df = pd.read_sql(QUERY,dfndb)
    csv_data = fn_db.read_data(df)
    import parameter_from_db #import/reload parameter_from_db.py file
    importlib.reload(parameter_from_db)


    #IF Value
    if dispdf.raw_data_class.iloc[0] == 'value':
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: VALUE***')
        col3.markdown(''+dispdf.raw_data.iloc[0]+'',unsafe_allow_html=True)
        col4.markdown(dispdf.unit_out.iloc[0])

    elif dispdf.raw_data_class.iloc[0] == 'array':
        # st.write('array')
        col1, col2, col3 = st.beta_columns(3)
        col1.markdown('***DATA: ARRAY***')
        disp_option = col2.radio("Display options",('Plot', 'Array'))
        csv_data = fn_db.read_data(df)
        c = csv_data[:,0]
        y = csv_data[:,1]
        x = c
        y = y
        if disp_option == 'Plot':
            disp_option2 = col3.radio("Axes scale",('Linear', 'Log'))
            if disp_option2 == 'Log':
                log = 'log'
            elif disp_option2 == 'Linear':
                log = 'linear'
            fn_plot.plotalt(x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'Array':
            csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
            csvdf

    elif dispdf.raw_data_class.iloc[0] == 'function':
        # st.write('array')
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: FUNCTION***')
        # Tlow = np.double(df.temp_range[0].lower)
        # Tlow
        # Tup = np.double(df.temp_range[0].upper)
        # Tup = Tup+0.001
        # tempslide = col2.slider('Temp [K]',np.float(Tlow),np.float(Tup))
        disp_option = col3.radio("Display options",('Plot', 'See Function'))
        c_low = float(df.input_range.to_numpy()[0].lower)+0.001
        c_max = float(df.input_range.to_numpy()[0].upper)-0.001
        c = np.linspace(c_low,c_max,10000)
        T = tempslide
        try:
            y = parameter_from_db.function(c,T) #run the function just written from the database
        except:
            y = parameter_from_db.function(c)
        x = c
        y = y
        if disp_option == 'Plot':
            disp_option2 = col4.radio("Axes scale",('Linear', 'Log'))
            if disp_option2 == 'Log':
                log = 'log'
            elif disp_option2 == 'Linear':
                log = 'linear'
            fn_plot.plotalt(x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'See Function':
            st.markdown('<h4>Parameter function:</h4>',unsafe_allow_html=True)
            source_foo = inspect.getsource(parameter_from_db)  # foo is normal function
            st.write(source_foo)


        #PAPER INFORMATION
    st.write('---')
    st.markdown('***PAPER***')
    st.markdown('<h3>'+dispdf.title.iloc[0]+'</h3>',unsafe_allow_html=True)
    col1, col2 = st.beta_columns(2)
    col1.markdown(dispdf.authors.iloc[0])
    if col2.button('Open paper URL'):
        webbrowser.open_new_tab(dispdf.url.iloc[0])
    #NOTES TEMPRANGE, & METHOD
    col1, col2, col3 = st.beta_columns(3)
    col1.markdown('***NOTES***')
    col1.write(dispdf.notes.iloc[0])
    col2.markdown('***TEMP RANGE*** [K]')
    col2.write(dispdf.temp_range.iloc[0])
    col3.markdown('***METHODS***')
    methoddf = dispdf.method_name
    methoddf = methoddf.astype(str) + ','
    col3.write(methoddf.to_string(index=False))


def page_advanced(state):
    st.title(":rocket: Advanced Queries")
    # display_state_values(state)

    st.write("---")
    st.write("Here are some examples, and how you can see what the full structure of the database schema is")
    st.write("---")

    @st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
    def init_connection():
        db_connection_string = {
        'address' : 'dfn-parameters.postgres.database.azure.com',
        'port' : '5432',
        'username' : 'testuser@dfn-parameters',
        'password' : 'testuserpassword',
        'dbname' : 'dfndb',
        }
        db_connection = fn_sql.sqlalchemy_connect(db_connection_string) #Make connection

        dfndb = db_connection['dbobject']
        return dfndb
    dfndb = init_connection()
    default_query = '''SELECT DISTINCT data.data_id,parameter.name as parameter, material.name as material, paper.paper_tag,data.raw_data, parameter.units_output, data.temp_range, data.notes
FROM data
JOIN paper ON paper.paper_id = data.paper_id
JOIN material ON material.material_id = data.material_id
JOIN parameter ON parameter.parameter_id = data.parameter_id
WHERE parameter.name = 'Maximum Concentration'
and material.class = 'cathode'
LIMIT 5
            '''

    if state.query is None:
        state.query = default_query
    st.markdown('<h3>Build SQL Query</h3>', unsafe_allow_html=True)
    form = st.form(key='Query',clear_on_submit=False)
    state.query = form.text_area('Note: "data.data_id" required',state.query,height=300)
    submit_button = form.form_submit_button(label='Run Statement')
    st.markdown('<h3>Results Table</h3>', unsafe_allow_html=True)
    df = pd.read_sql(state.query,dfndb)
    df_result = st.dataframe(df,height = 1000)

    # if state.data_id is None:
    #     options = df.data_id.to_numpy()
    # else:
    #     options = np.append([state.data_i],df.data_id.to_numpy())
    options = df.data_id
    if submit_button:
        df = pd.read_sql(state.query,dfndb)
        df_result.empty()
        df_result = st.dataframe(df,height = 1000)
        options = df.data_id
        # options = np.append([state.data_i],df.data_id.to_numpy())

    # submit_button
    ## SELECT A SPECIFIC DATA_ID TO EXPAND:

    st.markdown('<h3>View Parameter</h3>', unsafe_allow_html=True)
    state.data_id = st.selectbox('Select data_id:',options)
    # st.write(state.data_id)
    # form = st.form(key='expandData',clear_on_submit=False)
    # state.data_id = form.selectbox('Choose row:',options)
    # submit_button = form.form_submit_button(label='Load Data')
    # if submit_button:
    QUERY = f'''
            SELECT DISTINCT data.data_id,
            data.raw_data_class,
            data.temp_range as temp_range,
            parameter.name as param_name,
            parameter.symbol as param_symbol,
            parameter.class as param_class,
            parameter.units_output as unit_out,
            parameter.units_input as unit_in,
             paper.paper_tag,
             paper.url,
             paper.title,
             paper.authors,
             data.raw_data,
             data.notes,
             method.name as method_name,
             method.description as method_desc,
             material.name as mat_name,
             material.class as mat_class,
             material.note as mat_note
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            JOIN data_method ON data.data_id = data_method.data_id
            JOIN method ON data_method.method_id = method.method_id
            WHERE data.data_id= %s
            '''%str(state.data_id)
    dispdf = pd.read_sql(QUERY,dfndb)
    # st.dataframe(dispdf.transpose(),height = 1000)
    st.write("---")
    #PARAMETER
    st.markdown('***PARAMETER***')
    col1, col2 = st.beta_columns(2)
    # col1.latex(dispdf.param_symbol.iloc[0][1:-1])
    col1.title(dispdf.param_symbol.iloc[0])
    col2.markdown('<h2>' + dispdf.param_class.iloc[0].title() + ' '+ dispdf.param_name.iloc[0]+ '</h2>',unsafe_allow_html=True)
    #MATERIAL
    st.markdown('***MATERIAL***')
    col1, col2 = st.beta_columns(2)
    col1.write(dispdf.mat_name.iloc[0])
    col2.write(dispdf.mat_note.iloc[0],unsafe_allow_html=True)

    st.write('---')
    #PLOTTING SHOWING Data
    log = 'linear'
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]

    QUERY = 'SELECT * FROM data WHERE data_id = %s;' %str(state.data_id)
    df = pd.read_sql(QUERY,dfndb)
    csv_data = fn_db.read_data(df)
    import parameter_from_db #import/reload parameter_from_db.py file
    importlib.reload(parameter_from_db)


    #IF Value
    if dispdf.raw_data_class.iloc[0] == 'value':
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: VALUE***')
        col3.markdown(''+dispdf.raw_data.iloc[0]+'',unsafe_allow_html=True)
        col4.markdown(dispdf.unit_out.iloc[0])

    elif dispdf.raw_data_class.iloc[0] == 'array':
        # st.write('array')
        col1, col2, col3 = st.beta_columns(3)
        col1.markdown('***DATA: ARRAY***')
        disp_option = col2.radio("Display options",('Plot', 'Array'))
        csv_data = fn_db.read_data(df)
        c = csv_data[:,0]
        y = csv_data[:,1]
        x = c
        y = y
        if disp_option == 'Plot':
            disp_option2 = col3.radio("Axes scale",('Linear', 'Log'))
            if disp_option2 == 'Log':
                log = 'log'
            elif disp_option2 == 'Linear':
                log = 'linear'
            fn_plot.plotalt(x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'Array':
            csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
            csvdf

    elif dispdf.raw_data_class.iloc[0] == 'function':
        # st.write('array')
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: FUNCTION***')
        # Tlow = np.double(df.temp_range[0].lower)
        # Tup = np.double(df.temp_range[0].upper)
        # Tup = Tup+0.001
        # tempslide = col2.slider('Temp [K]',np.float(Tlow),np.float(Tup))
        disp_option = col3.radio("Display options",('Plot', 'See Function'))
        c_low = float(df.input_range.to_numpy()[0].lower)+0.001
        c_max = float(df.input_range.to_numpy()[0].upper)-0.001
        c = np.linspace(c_low,c_max,10000)
        T = tempslide
        try:
            y = parameter_from_db.function(c,T) #run the function just written from the database
        except:
            y = parameter_from_db.function(c)
        x = c
        y = y
        if disp_option == 'Plot':
            disp_option2 = col4.radio("Axes scale",('Linear', 'Log'))
            if disp_option2 == 'Log':
                log = 'log'
            elif disp_option2 == 'Linear':
                log = 'linear'
            fn_plot.plotalt(x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'See Function':
            st.markdown('<h4>Parameter function:</h4>',unsafe_allow_html=True)
            source_foo = inspect.getsource(parameter_from_db)  # foo is normal function
            st.write(source_foo)


        #PAPER INFORMATION
    st.write('---')
    st.markdown('***PAPER***')
    st.markdown('<h3>'+dispdf.title.iloc[0]+'</h3>',unsafe_allow_html=True)
    col1, col2 = st.beta_columns(2)
    col1.markdown(dispdf.authors.iloc[0])
    if col2.button('Open paper URL'):
        webbrowser.open_new_tab(dispdf.url.iloc[0])
    #NOTES TEMPRANGE, & METHOD
    col1, col2, col3 = st.beta_columns(3)
    col1.markdown('***NOTES***')
    col1.write(dispdf.notes.iloc[0])
    col2.markdown('***TEMP RANGE*** [K]')
    col2.write(dispdf.temp_range.iloc[0])
    col3.markdown('***METHODS***')
    methoddf = dispdf.method_name
    methoddf = methoddf.astype(str) + ','
    col3.write(methoddf.to_string(index=False))


def display_state_values(state):
    st.write("Query Input: ", state.query)

    # st.dataframe(state.queryresult)
    # st.write("Slider state:", state.slider)
    # st.write("Radio state:", state.radio)
    # st.write("Checkbox state:", state.checkbox)
    # st.write("Selectbox state:", state.selectbox)
    # st.write("Multiselect state:", state.multiselect)
    #
    # for i in range(3):
    #     st.write(f"Value {i}:", state[f"State value {i}"])

    if st.button("Clear state"):
        state.clear()


class _SessionState:
    def __init__(self, session, hash_funcs):
        """Initialize SessionState instance."""
        self.__dict__["_state"] = {
            "data": {},
            "hash": None,
            "hasher": _CodeHasher(hash_funcs),
            "is_rerun": False,
            "session": session,
        }

    def __call__(self, **kwargs):
        """Initialize state data once."""
        for item, value in kwargs.items():
            if item not in self._state["data"]:
                self._state["data"][item] = value

    def __getitem__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __getattr__(self, item):
        """Return a saved state value, None if item is undefined."""
        return self._state["data"].get(item, None)

    def __setitem__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def __setattr__(self, item, value):
        """Set state value."""
        self._state["data"][item] = value

    def clear(self):
        """Clear session state and request a rerun."""
        self._state["data"].clear()
        self._state["session"].request_rerun()

    def sync(self):
        """Rerun the app with all state values up to date from the beginning to fix rollbacks."""

        # Ensure to rerun only once to avoid infinite loops
        # caused by a constantly changing state value at each run.
        #
        # Example: state.value += 1
        if self._state["is_rerun"]:
            self._state["is_rerun"] = False

        elif self._state["hash"] is not None:
            if self._state["hash"] != self._state["hasher"].to_bytes(self._state["data"], None):
                self._state["is_rerun"] = True
                self._state["session"].request_rerun()

        self._state["hash"] = self._state["hasher"].to_bytes(self._state["data"], None)


def _get_session():
    session_id = get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")

    return session_info.session


def _get_state(hash_funcs=None):
    session = _get_session()

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = _SessionState(session, hash_funcs)

    return session._custom_session_state


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
