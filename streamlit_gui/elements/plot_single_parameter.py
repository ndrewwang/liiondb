import streamlit as st
import psycopg2
import inspect
import sys
import os
import importlib
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import pandas as pd
import numpy as np
import webbrowser
import altair as alt
import markdown
import base64

def write(dispdf,df,session_state):
    if 'radio_dispoptions' not in st.session_state:
        st.session_state.radio_dispoptions = 0
    dfndb, db_connection = fn_db.liiondb()
    st.session_state = session_state
    data_id = int(dispdf.data_id[0])
    st.write('---')
    #------------------------------------- PLOTTING  -------------------------------------
    log = 'linear'
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]
    csv_data = fn_db.read_data(df)
    import parameter_from_db
    importlib.reload(tmp.parameter_from_db)
    # import streamlit_gui.elements.parameter_from_db#import/reload parameter_from_db.py file
    # importlib.reload(streamlit_gui.elements.parameter_from_db)
    form = st.form(key='plot_form')
    #IF Value
    if dispdf.raw_data_class.iloc[0] == 'value':
        col1, col2, col3, col4 = form.columns(4)
        col1.markdown('***DATA: VALUE***')
        if float(dispdf.raw_data.iloc[0])<1E-4:
                col3.markdown("{:.2e}".format(float(dispdf.raw_data.iloc[0])),unsafe_allow_html=True)
        else:
            col3.markdown(''+dispdf.raw_data.iloc[0]+'',unsafe_allow_html=True)
        col4.markdown(dispdf.unit_out.iloc[0])
        form.form_submit_button('')

    #IF ARRAY
    elif dispdf.raw_data_class.iloc[0] == 'array':
        col1, col2, col3 = form.columns(3)
        col1.markdown('***DATA: ARRAY***')
        radio_dispoptions = ['Plot linear scale','Plot log scale', 'Array']
        disp_option = col3.radio("Display options",radio_dispoptions,st.session_state.radio_dispoptions)
        col3.form_submit_button('Refresh view',on_click = append_current_count)

        c = csv_data[:,0]
        y = csv_data[:,1]
        x = c
        y = y
        if disp_option == 'Plot log scale':
            log = 'log'
            fn_plot.plot_single(form,x,y,log,mat_class,param_name,unit_in,unit_out)
        elif disp_option == 'Plot linear scale':
            log = 'linear'
            fn_plot.plot_single(form,x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'Array':
            csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
            csvdf.iloc[:, 0] = pd.to_numeric(csvdf.iloc[:, 0], downcast="float")
            form.write(csvdf.style.format("{:.2e}"))

        csv_download(form,csv_data,unit_in,unit_out)

    # IF FUNCTION
    elif dispdf.raw_data_class.iloc[0] == 'function':
        col1, col2, col3 = form.columns(3)
        col1.markdown('***DATA: FUNCTION***')
        Tlow = np.float(df.temp_range[0].lower)
        Tup = np.float(df.temp_range[0].upper)
        Tup = Tup+0.001
        slidevalue = col3.slider('Temp [K]',np.float(Tlow),np.float(Tup),step=np.float(1))
        radio_dispoptions = ['Plot linear scale','Plot log scale', 'See function']
        disp_option = col2.radio("Display options",radio_dispoptions)
        col3.form_submit_button('Refresh view',on_click = append_current_count)

        c_low = float(df.input_range.to_numpy()[0].lower)+0.001
        c_max = float(df.input_range.to_numpy()[0].upper)-0.001
        c = np.linspace(c_low,c_max,1000)
        T = slidevalue
        try:
            # y = streamlit_gui.elements.parameter_from_db.function(c,T) #run the function just written from the database
            y = tmp.parameter_from_db.function(c,T) #run the function just written from the database

        except:
            # y = streamlit_gui.elements.parameter_from_db.function(c)
            y = tmp.parameter_from_db.function(c)
        x = c
        y = y

        if disp_option == 'Plot log scale':
            log = 'log'
            fn_plot.plot_single(form,x,y,log,mat_class,param_name,unit_in,unit_out)
        elif disp_option == 'Plot linear scale':
            log = 'linear'
            fn_plot.plot_single(form,x,y,log,mat_class,param_name,unit_in,unit_out)
        if disp_option == 'See function':
            import textwrap
            form.markdown('<h4>Parameter function:</h4>',unsafe_allow_html=True)
            source_foo = inspect.getsource(streamlit_gui.elements.parameter_from_db)  # foo is normal function
            nlines = source_foo.count('\n')
            user_input = form.text_area("", source_foo,height=23*nlines)

        param_fn_download(form)

    return st.session_state

    #
    # elif dispdf.raw_data_class.iloc[0] == 'function':
    #     col1, col2, col3, col4 = st.columns(4)
    #     col1.markdown('***DATA: FUNCTION***')
    #     Tlow = np.double(df.temp_range[0].lower)
    #     Tup = np.double(df.temp_range[0].upper)
    #     Tup = Tup+0.001
    #     tempslide = col2.slider('Temp [K]',np.float(Tlow),np.float(Tup))
    #     st.session_state.disp_option_function = col3.radio("Display options",('Plot', 'See Function'))
    #     c_low = float(df.input_range.to_numpy()[0].lower)+0.001
    #     c_max = float(df.input_range.to_numpy()[0].upper)-0.001
    #     c = np.linspace(c_low,c_max,100)
    #     T = tempslide
    #     try:
    #         y = parameter_from_db.function(c,T) #run the function just written from the database
    #     except:
    #         y = parameter_from_db.function(c)
    #     x = c
    #     y = y
    #     if st.session_state.disp_option_function == 'Plot':
    #         st.session_state.disp_option_function_scale = col4.radio("Axes scale",('Linear', 'Log'))
    #         if st.session_state.disp_option_function_scale == 'Log':
    #             log = 'log'
    #         elif st.session_state.disp_option_function_scale == 'Linear':
    #             log = 'linear'
    #         fn_plot.plot_single(x,y,log,mat_class,param_name,unit_in,unit_out)
    #     if st.session_state.disp_option_function == 'See Function':
    #         st.markdown('<h4>Parameter function:</h4>',unsafe_allow_html=True)
    #         source_foo = inspect.getsource(parameter_from_db)  # foo is normal function
    #         st.write(source_foo)
    #
    #     #-------------------------------------DOWNLOADD  PYTHON FUNCTION  -------------------------------------
    #     source_foo = inspect.getsource(parameter_from_db)
    #     b64 = base64.b64encode(source_foo.encode()).decode()  # some strings <-> bytes conversions necessary here
    #     href = f'<a href="data:file/csv;base64,{b64}">**[Download Python Function]**</a> right-click and save as &lt;function_name&gt;.py'
    #     st.markdown(href, unsafe_allow_html=True)


def append_current_count():
    st.session_state.count_array.append(st.session_state.count)

def param_fn_download(form):
    import streamlit_gui.elements.parameter_from_db #import/reload parameter_from_db.py file
    source_foo = inspect.getsource(streamlit_gui.elements.parameter_from_db)
    b64 = base64.b64encode(source_foo.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">**[Download Python Function]**</a> right-click and save as &lt;function_name&gt;.py'
    form.markdown(href, unsafe_allow_html=True)

def csv_download(form,csv_data,unit_in,unit_out):
    csvdf = pd.DataFrame(csv_data,columns=[unit_in, unit_out])
    csv = csvdf.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">**[Download CSV]**</a> right-click and save as &lt;array_name&gt;.csv'
    form.markdown(href, unsafe_allow_html=True)
