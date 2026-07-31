import math
import streamlit as st
import pandas as pd
import numpy as np
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import streamlit_gui.queries as queries

# PARAMETER DATA DISPLAY & PLOT ====================
#
# Function-type parameters are stored in the database as Python source
# blobs. The original app wrote each blob to a .py file on disk and
# re-imported it with importlib on every rerun; here the blob is compiled
# in memory once (fn_db.evaluate_function -> lru_cache) and each evaluated
# curve is cached by (data_id, T), so moving the temperature slider only
# computes each curve once.

def write(dispdf, df):
    data_id = int(dispdf.data_id.iloc[0])
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]
    raw_class = dispdf.raw_data_class.iloc[0]
    st.write('---')

    # ----- VALUE -----
    if raw_class == 'value':
        col1, col2 = st.columns(2)
        col1.markdown('***DATA: VALUE***')
        value = float(dispdf.raw_data.iloc[0])
        shown = '{:.2e}'.format(value) if abs(value) < 1e-4 else dispdf.raw_data.iloc[0]
        col2.metric(label='[' + str(unit_out) + ']', value=shown)

    # ----- ARRAY -----
    elif raw_class == 'array':
        col1, col2 = st.columns([1, 2])
        col1.markdown('***DATA: ARRAY***')
        disp_option = col2.radio('Display options',
                                 ['Plot linear scale', 'Plot log scale', 'Array'],
                                 horizontal=True, key='radio_array_%s' % data_id)
        csv_data = queries.parse_array(df.raw_data.iloc[0])
        x, y = csv_data[:, 0], csv_data[:, 1]
        if disp_option == 'Plot log scale':
            fn_plot.plot_single(st, x, y, 'log', mat_class, param_name, unit_in, unit_out)
        elif disp_option == 'Plot linear scale':
            fn_plot.plot_single(st, x, y, 'linear', mat_class, param_name, unit_in, unit_out)
        else:
            csvdf = pd.DataFrame(csv_data, columns=[str(unit_in), str(unit_out)])
            st.dataframe(csvdf.style.format('{:.4e}'), height=400)
        csvdf = pd.DataFrame(csv_data, columns=[str(unit_in), str(unit_out)])
        st.download_button('Download CSV', csvdf.to_csv(index=False),
                           file_name='liiondb_data_%s.csv' % data_id, mime='text/csv')

    # ----- FUNCTION -----
    elif raw_class == 'function':
        col1, col2, col3 = st.columns([1, 1, 1])
        col1.markdown('***DATA: FUNCTION***')
        disp_option = col2.radio('Display options',
                                 ['Plot linear scale', 'Plot log scale', 'See function'],
                                 horizontal=True, key='radio_fn_%s' % data_id)

        T_low, T_up = fn_db.parse_range(df.temp_range.iloc[0])
        has_T_range = (T_low is not None and T_up is not None
                       and math.isfinite(T_low) and math.isfinite(T_up))
        if has_T_range and T_up > T_low:
            default_T = min(max(298.0, T_low), T_up)
            T = col3.slider('Temp [K]', float(T_low), float(T_up), float(default_T), step=1.0,
                            key='slider_T_%s' % data_id)
        else:
            T = float(T_low) if has_T_range else 298.0
            col3.caption('Temperature: %g K%s' % (T, '' if has_T_range else ' (no range reported)'))

        x, y = queries.evaluate_function_curve(data_id, T)
        if disp_option == 'Plot log scale':
            fn_plot.plot_single(st, x, y, 'log', mat_class, param_name, unit_in, unit_out)
        elif disp_option == 'Plot linear scale':
            fn_plot.plot_single(st, x, y, 'linear', mat_class, param_name, unit_in, unit_out)
        else:
            st.markdown('<h4>Parameter function:</h4>', unsafe_allow_html=True)
            st.code(fn_db.function_source(df['function'].iloc[0]), language='python')

        st.download_button('Download Python function',
                           fn_db.function_source(df['function'].iloc[0]),
                           file_name='liiondb_function_%s.py' % data_id, mime='text/x-python')
