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
import markdown
import base64
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import streamlit_gui.elements.paper_info
import streamlit_gui.elements.plot_single_parameter

def write(selections,session_state):
    dfndb, db_connection = fn_db.liiondb()
    param_check(selections)
    data_id_list = [int(i.split(' |')[0]) for i in selections]
    st.session_state = session_state
    dfndb, db_connection = fn_db.liiondb()

    #PARAMETER TITLE
    data_id = data_id_list[0]
    st.session_state.dispdf = query_to_display(data_id)
    dispdf = st.session_state.dispdf
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    legend_list = [(i.replace(' '+param_name+ '   |','')) for i in selections]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]

    st.markdown('***PARAMETER COMPARISON***')
    col1, col2 = st.columns(2)
    col1.title(dispdf.param_symbol.iloc[0])
    col2.markdown('<h2>' + dispdf.param_name.iloc[0].capitalize()+ '</h2>',unsafe_allow_html=True)

    #FORM INFO
    if 'radio_dispoptions' not in st.session_state:
        st.session_state.radio_dispoptions = 0

    form = st.form(key='plot_form')
    col1, col2, col3, col4 = form.columns(4)
    radio_dispoptions = ['Plot linear scale','Plot log scale']
    disp_option = col2.radio("Display options",radio_dispoptions,st.session_state.radio_dispoptions)
    col3.form_submit_button('Refresh view',on_click = append_current_count)

    if disp_option == 'Plot log scale':
        log = 'log'
    elif disp_option == 'Plot linear scale':
        log = 'linear'

    # FIGURE PROPERTIES
    w = 9
    h = 5
    d = 150
    fig = plt.figure(figsize=(w, h), dpi=d)
    hfont = {'fontname':'sans serif'}
    # hfont = {'fontname':'helvetica'}
    # Label font sizes
    SMALL_SIZE = 7
    MEDIUM_SIZE = 9
    BIGGER_SIZE = 15
    border_width = 0.5

    # form.write(T)

    # LOOP THROUGH FOR COMPARISON
    for i,data_id in enumerate(data_id_list):
        leg_string = legend_list[i]
        df = perform_data_query(data_id)
        csv_data = fn_db.gui_read_data(df)

        import importlib.util
        spec = importlib.util.spec_from_file_location("parameter_from_db", "/tmp/parameter_from_db.py")
        parameter_from_db = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parameter_from_db)

        #IF FUNCTION NEEDS A TEMPERATURE, TRY 298 THEN THE MEAN OF THE 2 LIMITS
        if df.raw_data_class[0] == 'function':
            T = 298
            Tlow = np.float(df.temp_range[0].lower)
            Tup = np.float(df.temp_range[0].upper)
            # form.write(Tlow)
            # form.write(Tup)
            if T<Tlow and T>Tup:
                T = (Tlow+Tup)/2
            c_low = float(df.input_range.to_numpy()[0].lower)+0.001
            c_max = float(df.input_range.to_numpy()[0].upper)-0.001
            c = np.linspace(c_low,c_max,1000) #SI Units mol/m3
            try:
                y = parameter_from_db.function(c,T) #run the function just written from the database
            except:
                y = parameter_from_db.function(c)
            x = c
            y = y
            plt.plot(x,y,'-',label=leg_string)

        elif df.raw_data_class[0] == 'array':
            c = csv_data[:,0]
            y = csv_data[:,1]
            x = c
            y = y
            if len(x)==1:
                plt.plot(x,y,'x-',label=leg_string)
            else:
                plt.plot(x,y,'-',label=leg_string)

        elif df.raw_data_class[0] == 'value':
            n = 10
            y = float(csv_data)
            y = y*np.linspace(1,1,n)
            c_low = float(df.input_range.to_numpy()[0].lower)
            c_max = float(df.input_range.to_numpy()[0].upper)
            c = np.linspace(c_low,c_max,n) #SI Units mol/m3
            x = c
            y = y
            plt.plot(x,y,'-',label=leg_string)



        xlabel = '['+ unit_in+']'
        ylabel = param_name + '  [' + unit_out + ']'
        # plt.plot(x,y,'-',color='#FF0066')

        ax = plt.gca()
        ax.yaxis.set_tick_params(width=border_width)
        ax.xaxis.set_tick_params(width=border_width)
        plt.minorticks_on()

        fontP = FontProperties()
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
        plt.rcParams['axes.linewidth'] = border_width
        plt.grid(b=True,which='both',axis='both',linewidth=border_width/2)

        if param_name == 'half cell ocv':
            vmin = 0
            vmax = 2
            ylabel = 'voltage [V]'
            xlabel = r'degree of lithiation $\theta$'
            if mat_class == 'positive':
                vmin = 3
                vmax = 4.5
            # plt.ylim(vmin,vmax)

        if param_name == 'diffusion coefficient' and mat_class != 'electrolyte':
            xlabel = r'degree of lithiation $\theta$'

        if mat_class == 'electrolyte':
            xlabel = 'concentration [mol*m^-3]'
            if param_name == 'ionic conductivity':
                plt.ylim(0,1.6)


        plt.ylabel(ylabel, **hfont,fontweight='bold')
        plt.xlabel(xlabel, **hfont,fontweight='bold')
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.yscale(log)
        # plt.show()
    form.pyplot(fig)


    return session_state

def append_current_count():
    st.session_state.count_array.append(st.session_state.count)

@st.cache
def param_check(selections): #selections pre data_id samplesdict
    selections = [(i.split(' | ')[1]) for i in selections] #get list of parameters
    if all(selections[0]==i for i in selections)==  False: #true if all parameter are good
        st.write('Please select data with the same parameter to compare')
        raise ValueError('Cannot plot comparison of different parameter types')
# @st.cache
def perform_data_query(data_id):
    dfndb, db_connection = fn_db.liiondb()
    QUERY = f'SELECT * FROM data WHERE data_id = {data_id}'
    df = pd.read_sql(QUERY,dfndb)
    return df
#
def check_refresh():
    refresh = False
    if len(st.session_state.count_array)>1:
        if st.session_state.count_array[-2]!=st.session_state.count_array[-1]:
            refresh = True
    return refresh


@st.cache
def query_to_display(data_id):
     dfndb, db_connection = fn_db.liiondb()

     QUERY = f'''
             SELECT DISTINCT data.data_id,
             data.raw_data_class,
             data.temp_range as temp_range,
             parameter.name as param_name,
             parameter.symbol as param_symbol,
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
             WHERE data.data_id = {data_id}
             '''
     QUERY_nomethod = f'''
             SELECT DISTINCT data.data_id,
             data.raw_data_class,
             data.temp_range as temp_range,
             parameter.name as param_name,
             parameter.symbol as param_symbol,
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
             WHERE data.data_id = {data_id}
             '''
     dispdf = pd.read_sql(QUERY,dfndb)
     if dispdf.size == 0:
         dispdf = pd.read_sql(QUERY_nomethod,dfndb)
     dispdf = convert_df_numrange(dispdf)
     return dispdf

@st.cache
def convert_df_numrange(df):
 import ast
 import numpy as np
 if 'temp_range' in df.keys():
     A = df.temp_range.astype(str) #convert to string
     df.temp_range = A
 elif 'input_range' in df.keys():
     A = df.input_range.astype(str) #convert to string
     df.input_range = A
 return df

if __name__ == "__main__":
    write()
