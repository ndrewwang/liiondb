import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

def plot_single(form,x,y,log,mat_class,param_name,unit_in,unit_out):
    # Plot display settings
    w = 7
    h = 4
    d = 150
    fig = plt.figure(figsize=(w, h), dpi=d)
    hfont = {'fontname':'sans serif'}
    # hfont = {'fontname':'helvetica'}


    # Label font sizes
    SMALL_SIZE = 7
    MEDIUM_SIZE = 9
    BIGGER_SIZE = 15
    border_width = 0.5

    xlabel = '['+ unit_in+']'
    ylabel = param_name + '  [' + unit_out + ']'
    if len(x)==1:
        plt.plot(x,y,'x-',color='#FF0066')
    else:
        plt.plot(x,y,'-',color='#FF0066')

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
        plt.ylim(vmin,vmax)

    if param_name == 'diffusion coefficient' and mat_class != 'electrolyte':
        xlabel = r'degree of lithiation $\theta$'

    if mat_class == 'electrolyte':
        xlabel = 'concentration [mol*m^-3]'
        if param_name == 'ionic conductivity':
            plt.ylim(0,1.6)


    plt.ylabel(ylabel, **hfont,fontweight='bold')
    plt.xlabel(xlabel, **hfont,fontweight='bold')
    plt.yscale(log)
    # plt.show()
    form.pyplot(fig)


# def plotalt(x,y,log,mat_class,param_name,unit_in,unit_out):
#             chart_data = pd.DataFrame({
#                                         'y': y,
#                                         'x': x})
#
#             if param_name == 'half cell ocv':
#                 vmin = 0
#                 vmax = 2
#                 if mat_class == 'positive':
#                     vmin = 3
#                     vmax = 4.5
#                 # st.line_chart(chart_data)
#                 c = alt.Chart(chart_data).mark_line(clip=True).encode(
#                     x=alt.X('x',axis=alt.Axis(title = 'degree of lithiation [x]'),scale=alt.Scale(domain=(0,1))),
#                     y=alt.Y('y',axis=alt.Axis(title = 'voltage [V]'),scale=alt.Scale(domain=(vmin,vmax),type=log, base=10)),
#                     color = alt.value("FF0066")
#                     ).configure_axis(
#                         labelFontSize = 15,
#                         titleFontSize = 18)
#
#                 st.altair_chart(c, use_container_width=True)
#
#             if param_name == 'diffusion coefficient':
#                 if mat_class != 'electrolyte':
#                 # st.line_chart(chart_data)
#                     c = alt.Chart(chart_data).mark_line(clip=True).encode(
#                         x=alt.X('x',axis=alt.Axis(title = 'degree of lithiation [x]'),scale=alt.Scale(domain=(0,1))),
#                         y=alt.Y('y',axis=alt.Axis(title = 'diffusion coefficient [m^2/s]'),scale=alt.Scale(type=log, base=10)),
#                         color = alt.value("FF0066")
#                         ).configure_axis(
#                             labelFontSize = 15,
#                             titleFontSize = 18)
#
#                     st.altair_chart(c, use_container_width=True)
#
#
#             if mat_class == 'electrolyte':
#                 # st.line_chart(chart_data)
#                 if param_name == 'ionic conductivity':
#                     c = alt.Chart(chart_data).mark_line(clip=True).encode(
#                         x=alt.X('x',axis=alt.Axis(title = 'concentration [mol*m^-3]')),
#                         y=alt.Y('y',axis=alt.Axis(title = param_name + ' ['+ unit_out+']'),scale=alt.Scale(type=log, base=10,domain=(0,1.6))),
#                         color = alt.value("FF0066")
#                         ).configure_axis(
#                             labelFontSize = 15,
#                             titleFontSize = 18).properties(height = 500)
#                 else:
#                     c = alt.Chart(chart_data).mark_line(clip=True).encode(
#                         x=alt.X('x',axis=alt.Axis(title = 'concentration [mol*m^-3]')),
#                         y=alt.Y('y',axis=alt.Axis(title = param_name + ' ['+ unit_out+']'),scale=alt.Scale(type=log, base=10)),
#                         color = alt.value("FF0066")
#                         ).configure_axis(
#                             labelFontSize = 15,
#                             titleFontSize = 18).properties(height = 500)
#                 st.altair_chart(c, use_container_width=True)
