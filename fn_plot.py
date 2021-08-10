import altair as alt
import pandas as pd
import numpy as np
import streamlit as st


def plotalt(x,y,log,mat_class,param_name,unit_in,unit_out):
            chart_data = pd.DataFrame({
                                        'y': y,
                                        'x': x})

            if param_name == 'Half Cell OCV':
                vmin = 0
                vmax = 2
                if mat_class == 'cathode':
                    vmin = 3
                    vmax = 4.5
                # st.line_chart(chart_data)
                c = alt.Chart(chart_data).mark_line(clip=True).encode(
                    x=alt.X('x',axis=alt.Axis(title = 'Degree of Lithiation [x]'),scale=alt.Scale(domain=(0,1))),
                    y=alt.Y('y',axis=alt.Axis(title = 'Voltage [V]'),scale=alt.Scale(domain=(vmin,vmax),type=log, base=10)),
                    color = alt.value("FF0066")
                    ).configure_axis(
                        labelFontSize = 15,
                        titleFontSize = 18)

                st.altair_chart(c, use_container_width=True)

            if param_name == 'Diffusion Coefficient':
                if mat_class != 'electrolyte':
                # st.line_chart(chart_data)
                    c = alt.Chart(chart_data).mark_line(clip=True).encode(
                        x=alt.X('x',axis=alt.Axis(title = 'Degree of Lithiation [x]'),scale=alt.Scale(domain=(0,1))),
                        y=alt.Y('y',axis=alt.Axis(title = 'Diffusion Coefficient [m^2/s]'),scale=alt.Scale(type=log, base=10)),
                        color = alt.value("FF0066")
                        ).configure_axis(
                            labelFontSize = 15,
                            titleFontSize = 18)

                    st.altair_chart(c, use_container_width=True)


            if mat_class == 'electrolyte':
                # st.line_chart(chart_data)
                if param_name == 'Ionic Conductivity':
                    c = alt.Chart(chart_data).mark_line(clip=True).encode(
                        x=alt.X('x',axis=alt.Axis(title = 'Concentration [mol*m^-3]')),
                        y=alt.Y('y',axis=alt.Axis(title = param_name + ' ['+ unit_out+']'),scale=alt.Scale(type=log, base=10,domain=(0,1.6))),
                        color = alt.value("FF0066")
                        ).configure_axis(
                            labelFontSize = 15,
                            titleFontSize = 18).properties(height = 500)
                else:
                    c = alt.Chart(chart_data).mark_line(clip=True).encode(
                        x=alt.X('x',axis=alt.Axis(title = 'Concentration [mol*m^-3]')),
                        y=alt.Y('y',axis=alt.Axis(title = param_name + ' ['+ unit_out+']'),scale=alt.Scale(type=log, base=10)),
                        color = alt.value("FF0066")
                        ).configure_axis(
                            labelFontSize = 15,
                            titleFontSize = 18).properties(height = 500)

                st.altair_chart(c, use_container_width=True)
