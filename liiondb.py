import streamlit as st
from streamlit.hashing import _CodeHasher
import psycopg2
import inspect
import sys
import os
import importlib
import fn_sql
import fn_db
import fn_plot
import pandas as pd
import numpy as np
import webbrowser
import altair as alt
import markdown
import base64

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

    # ================ SIDE BAR PAGES AND TEXT ===============================
    pages = {
        "Parameter Dashboard": page_dashboard,
        "Advanced Queries": page_advanced,
    }
    st.sidebar.title(":battery: LiionDB (ALPHA)")
    st.sidebar.markdown('<h2>DFN Parameter Database</h2>', unsafe_allow_html=True)
    page = st.sidebar.radio("Select your page", tuple(pages.keys()))
    # Display the selected page with the session state
    pages[page](state)
    # Mandatory to avoid rollbacks with widgets, must be called at the end of your app
    state.sync()
    st.sidebar.markdown('<h3>Info</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "This interactive database of DFN-type battery model parameters "
        "accompanies the review manuscript: "
        "[**Parameterising Continuum-Level Li-ion Battery Models**.](https://www.overleaf.com/project/5ed63d9378cbf700018a2018)"
        " If you use LiionDB in your work, please cite our paper at: "
        "[doi.org](https://www.doi.org/)")
    st.sidebar.markdown('<h3>About</h3>', unsafe_allow_html=True)
    st.sidebar.info(
        "LiionDB is a part of the "
        "[**Multi-Scale Modelling**](https://www.faraday.ac.uk/research/lithium-ion/battery-system-modelling/)"
        " project within "
        "[**The Faraday Institution**.](https://www.faraday.ac.uk/)")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SIMPLE QUERY BUILDER  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def page_dashboard(state):
    st.title(":mag_right: Parameter Dashboard")
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
    # ===============================DROP DOWN SELECTION CHOICES  ===============================


    #--------------------------------- MATERIAL CLASS DROPDOWN ---------------------------------
    QUERY = '''
            SELECT DISTINCT material.class
            FROM material
            '''
    df = pd.read_sql(QUERY,dfndb)
    classdf = df
    state.dash_mat_type = col1.selectbox('1. Material Type',classdf)

    #--------------------------------- PARAMETER DROPDOWN ---------------------------------
    QUERY = f'''
            SELECT DISTINCT parameter.name
            FROM parameter
            WHERE parameter.class = '{state.dash_mat_type}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    paramdf = df
    state.dash_param_name = col2.selectbox('2. Parameter',paramdf)

    #---------------------------------MATERIAL DROPDOWN ---------------------------------
    QUERY = f'''
            SELECT DISTINCT material.name
            FROM material
            JOIN data ON data.material_id = material.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE material.class = '{state.dash_mat_type}'
            AND parameter.name = '{state.dash_param_name}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    matdf = df
    state.dash_mat_name = col3.selectbox('3. Material Name',matdf)

    #---------------------------------SPECIFIC PAPER DROPDOWN ---------------------------------
    QUERY = f'''
            SELECT DISTINCT paper.paper_tag
            FROM paper
            JOIN data ON data.paper_id = paper.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE material.class = '{state.dash_mat_type}'
            AND parameter.name = '{state.dash_param_name}'
            AND material.name = '{state.dash_mat_name}'
            '''
    df = pd.read_sql(QUERY,dfndb)
    papdf = df
    state.dash_paper_name = col4.selectbox('4. Paper Source',papdf)

    #=============================== QUERY RESULTS TABLE ===============================
    st.markdown('<h3>Results Table</h3>', unsafe_allow_html=True)
    state.dash_dashquery = f'''SELECT DISTINCT data.data_id,parameter.name as parameter, material.name as material, paper.paper_tag,data.raw_data, parameter.units_output, data.temp_range, data.notes
    FROM data
    JOIN paper ON paper.paper_id = data.paper_id
    JOIN material ON material.material_id = data.material_id
    JOIN parameter ON parameter.parameter_id = data.parameter_id
    WHERE parameter.name = '{state.dash_param_name}'
    AND material.name = '{state.dash_mat_name}'
    AND paper.paper_tag = '{state.dash_paper_name}'
                '''
    df = pd.read_sql(state.dash_dashquery,dfndb)
    df_result = st.dataframe(df.head(1),height = 1000)
    # df_result = st.dataframe(df,height = 1000)
    state.dash_data_id = df.data_id.iloc[0]
    # st.write(state.dash_data_id)
    # form = st.form(key='expandData',clear_on_submit=False)
    # state.dash_data_id = form.selectbox('Choose row:',options)
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
            '''%str(state.dash_data_id)
    QUERY_nomethod = f'''
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
             material.name as mat_name,
             material.class as mat_class,
             material.note as mat_note
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE data.data_id = '{state.data_id}'
            '''
    dispdf = pd.read_sql(QUERY,dfndb)
    if dispdf.size == 0:
        dispdf = pd.read_sql(QUERY_nomethod,dfndb)
    # st.dataframe(dispdf.transpose(),height = 1000)
    st.write("---")
    #=============================== DISPLAY DATA PRETTY  ===============================
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
    #------------------------------------- PLOTTING  -------------------------------------
    log = 'linear'
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]

    QUERY = 'SELECT * FROM data WHERE data_id = %s;' %str(state.dash_data_id)
    df = pd.read_sql(QUERY,dfndb)
    csv_data = fn_db.read_data(df)
    import parameter_from_db #import/reload parameter_from_db.py file
    importlib.reload(parameter_from_db)


    #IF Value
    if dispdf.raw_data_class.iloc[0] == 'value':
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: VALUE***')
        if float(dispdf.raw_data.iloc[0])<1E-4:
                col3.markdown("{:.2e}".format(float(dispdf.raw_data.iloc[0])),unsafe_allow_html=True)
        else:
            col3.markdown(''+dispdf.raw_data.iloc[0]+'',unsafe_allow_html=True)
        col4.markdown(dispdf.unit_out.iloc[0])

    elif dispdf.raw_data_class.iloc[0] == 'array':
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
            csvdf.iloc[:, 0] = pd.to_numeric(csvdf.iloc[:, 0], downcast="float")
            st.write(csvdf.style.format("{:.2e}"))

        #------------------------------------- DOWNLOAD CSV  -------------------------------------
        csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
        csv = csvdf.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">**[Download CSV]**</a> right-click and save as &lt;array_name&gt;.csv'
        st.markdown(href, unsafe_allow_html=True)

    elif dispdf.raw_data_class.iloc[0] == 'function':
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: FUNCTION***')
        Tlow = np.double(df.temp_range[0].lower)
        Tup = np.double(df.temp_range[0].upper)
        Tup = Tup+0.001
        tempslide = col2.slider('Temp [K]',np.float(Tlow),np.float(Tup))
        disp_option = col3.radio("Display options",('Plot', 'See Function'))
        c_low = float(df.input_range.to_numpy()[0].lower)+0.001
        c_max = float(df.input_range.to_numpy()[0].upper)-0.001
        c = np.linspace(c_low,c_max,100)
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
        #------------------------------------- FUNCTION STRING  -------------------------------------
        if disp_option == 'See Function':
            st.markdown('<h4>Parameter function:</h4>',unsafe_allow_html=True)
            st.markdown('#')
            source_foo = inspect.getsource(parameter_from_db)  # foo is normal function
            st.write(source_foo)

        #-------------------------------------DOWNLOADD  PYTHON FUNCTION  -------------------------------------
        source_foo = inspect.getsource(parameter_from_db)
        b64 = base64.b64encode(source_foo.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">**[Download Python Function]**</a> right-click and save as &lt;function_name&gt;.py'
        st.markdown(href, unsafe_allow_html=True)


    #------------------------------------- PAPER INFORMATION  -------------------------------------
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
    try:
        methoddf = dispdf.method_name
        methoddf = methoddf.astype(str) + ','
        col3.write(methoddf.to_string(index=False))
    except:
        col3.write('No method available')
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ADVANCED QUERIES %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def page_advanced(state):
    st.title(":rocket: Advanced Queries")
    # display_state_values(state)
    #=============================== EXAMPLE QUERIES  ===============================
    samplesdict = {
    "OCV curves for cathodes with higher than 50% nickel content" :  '''
        SELECT DISTINCT data.data_id,parameter.name, material.name, paper.paper_tag,data.raw_data, parameter.units_output, data.temp_range
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'half cell ocv'
        AND material.ni > 0.5
        ''',
    "See all parameters available in LiionDB": '''
        SELECT * FROM parameter
        ''',
    "Li diffusivities in graphite that are valid at 10 °C": '''
        SELECT DISTINCT data.data_id,parameter.name, material.name, paper.paper_tag, paper.doi, data.temp_range
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'diffusion coefficient'
        AND material.class = 'negative'
        AND material.gr = 1
        AND 283 BETWEEN lower(data.temp_range) AND upper(data.temp_range)
        ''',
    "See all separator porosities": '''
        SELECT DISTINCT data.data_id,parameter.name, material.name, paper.paper_tag,data.raw_data
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE parameter.name = 'porosity'
        AND material.class = 'separator'
        ''',
    "All papers that publish parameters on LFP": '''
        SELECT DISTINCT paper.paper_tag, paper.title, paper.doi
        FROM paper
        JOIN data ON data.paper_id = paper.paper_id
        JOIN material ON data.material_id = material.material_id
        WHERE material.note = 'LiFePO4'
        ''',
    "Parameters that have been measured with EIS": '''
        SELECT DISTINCT parameter.name
        FROM parameter
        JOIN data ON data.parameter_id = parameter.parameter_id
        JOIN data_method ON data.data_id = data_method.data_id
        JOIN method ON data_method.method_id = method.method_id
        WHERE  method.name = 'EIS'
        ''',
    "Full electrolyte parameterizations": '''
        SELECT DISTINCT material.name, paper.paper_tag, parameter.name as param_name
        FROM material
        JOIN data ON data.material_id = material.material_id
        JOIN paper ON data.paper_id = paper.paper_id
        JOIN parameter ON data.parameter_id = parameter.parameter_id
        WHERE material.class = 'electrolyte'
        AND parameter.name IN ('ionic conductivity','diffusion coefficient','transference number','thermodynamic factor')
        LIMIT 5
        ''',
    "See the Doyle 1996 paper parameters": '''
        SELECT DISTINCT data.data_id,parameter.name, material.name, paper.paper_tag,data.raw_data, parameter.units_output, data.notes
        FROM data
        JOIN paper ON paper.paper_id = data.paper_id
        JOIN material ON material.material_id = data.material_id
        JOIN parameter ON parameter.parameter_id = data.parameter_id
        WHERE paper.paper_tag = 'Doyle1996'
        '''}

    st.write("---")
    form = st.form(key='examplesqlform')
    the_example = form.selectbox('Choose some example queries from this drop down list to get started!',list(samplesdict.keys()))
    submit_example = form.form_submit_button('Load into query box below')

    st.write("---")
    #=============================== QUERY BOX  ===============================
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
WHERE parameter.name = 'half cell ocv'
and material.class = 'positive'
LIMIT 5
            '''

    if state.query is None:
        state.query = default_query

    if submit_example:
            state.query = samplesdict[the_example]

    st.markdown('<h3>Build SQL Query</h3>', unsafe_allow_html=True)
    form = st.form(key='Query',clear_on_submit=False)
    state.query = form.text_area('Note: Selecting "data.data_id" is required to view parameters',state.query,height=300)
    submit_button = form.form_submit_button(label='Run Statement')
    st.markdown('<h3>Results Table</h3>', unsafe_allow_html=True)
    df = pd.read_sql(state.query,dfndb)
    df_result = st.dataframe(df,height = 1000)
    # df

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
            WHERE data.data_id = '{state.data_id}'
            '''
    QUERY_nomethod = f'''
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
             material.name as mat_name,
             material.class as mat_class,
             material.note as mat_note
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE data.data_id = '{state.data_id}'
            '''
    dispdf = pd.read_sql(QUERY,dfndb)
    if dispdf.size == 0:
        dispdf = pd.read_sql(QUERY_nomethod,dfndb)

    # st.dataframe(dispdf.transpose(),height = 1000)
    st.write("---")
    #=============================== DISPLAY DATA PRETTY  ===============================
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
    #------------------------------------- PLOTTING  -------------------------------------
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
        if float(dispdf.raw_data.iloc[0])<1E-4:
                col3.markdown("{:.2e}".format(float(dispdf.raw_data.iloc[0])),unsafe_allow_html=True)
        else:
            col3.markdown(''+dispdf.raw_data.iloc[0]+'',unsafe_allow_html=True)
        col4.markdown(dispdf.unit_out.iloc[0])

    elif dispdf.raw_data_class.iloc[0] == 'array':
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
            csvdf.iloc[:, 0] = pd.to_numeric(csvdf.iloc[:, 0], downcast="float")
            st.write(csvdf.style.format("{:.2e}"))

        #------------------------------------- DOWNLOAD CSV  -------------------------------------
        csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
        csv = csvdf.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">**[Download CSV]**</a> right-click and save as &lt;array_name&gt;.csv'
        st.markdown(href, unsafe_allow_html=True)

    elif dispdf.raw_data_class.iloc[0] == 'function':
        col1, col2, col3, col4 = st.beta_columns(4)
        col1.markdown('***DATA: FUNCTION***')
        Tlow = np.double(df.temp_range[0].lower)
        Tup = np.double(df.temp_range[0].upper)
        Tup = Tup+0.001
        tempslide = col2.slider('Temp [K]',np.float(Tlow),np.float(Tup))
        disp_option = col3.radio("Display options",('Plot', 'See Function'))
        c_low = float(df.input_range.to_numpy()[0].lower)+0.001
        c_max = float(df.input_range.to_numpy()[0].upper)-0.001
        c = np.linspace(c_low,c_max,100)
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

        #-------------------------------------DOWNLOADD  PYTHON FUNCTION  -------------------------------------
        source_foo = inspect.getsource(parameter_from_db)
        b64 = base64.b64encode(source_foo.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">**[Download Python Function]**</a> right-click and save as &lt;function_name&gt;.py'
        st.markdown(href, unsafe_allow_html=True)



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
    try:
        methoddf = dispdf.method_name
        methoddf = methoddf.astype(str) + ','
        col3.write(methoddf.to_string(index=False))
    except:
        col3.write('No method available')


def display_state_values(state):
    st.write("Query Input: ", state.query)

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
