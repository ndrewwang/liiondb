import math
import streamlit as st
import numpy as np
import functions.fn_db as fn_db
import functions.fn_plot as fn_plot
import streamlit_gui.queries as queries

# MULTI-PARAMETER COMPARISON ====================

def write(selections):
    parsed = [queries.parse_option(s) for s in selections]
    if not param_check(parsed):
        return

    data_id = parsed[0]['data_id']
    dispdf = queries.query_to_display(data_id)
    mat_class = dispdf.mat_class.iloc[0]
    param_name = dispdf.param_name.iloc[0]
    unit_in = dispdf.unit_in.iloc[0]
    unit_out = dispdf.unit_out.iloc[0]

    st.markdown('***PARAMETER COMPARISON***')
    col1, col2 = st.columns(2)
    col1.title(dispdf.param_symbol.iloc[0])
    col2.markdown('<h2>' + dispdf.param_name.iloc[0].capitalize() + '</h2>', unsafe_allow_html=True)

    disp_option = st.radio('Display options', ['Plot linear scale', 'Plot log scale'],
                           horizontal=True, key='radio_multi')
    log = 'log' if disp_option == 'Plot log scale' else 'linear'

    curves = []
    for p in parsed:
        # data_id in the label keeps curves distinct even when several
        # datasets share the same material and paper (common in the DB) —
        # identical labels would otherwise be merged into one line by the
        # color grouping in fn_plot.plot_multi
        label = '%s (%s) #%s' % (p['material'], p['paper'], p['data_id'])
        df = queries.data_row(p['data_id'])
        raw_class = df.raw_data_class.iloc[0]

        if raw_class == 'function':
            # try 298 K, clamped into the function's reported temperature range
            T_low, T_up = fn_db.parse_range(df.temp_range.iloc[0])
            T = 298.0
            if T_low is not None and T_up is not None and math.isfinite(T_low) and math.isfinite(T_up):
                T = min(max(T, T_low), T_up)
            x, y = queries.evaluate_function_curve(p['data_id'], T)
            curves.append((label, x, y))

        elif raw_class == 'array':
            csv_data = queries.parse_array(df.raw_data.iloc[0])
            curves.append((label, csv_data[:, 0], csv_data[:, 1]))

        elif raw_class == 'value':
            value = float(df.raw_data.iloc[0])
            c_low, c_max = fn_db.parse_range(df.input_range.iloc[0], default=(0.0, 1.0))
            if not (math.isfinite(c_low) and math.isfinite(c_max)) or c_low == c_max:
                c_low, c_max = 0.0, 1.0
            x = np.linspace(c_low, c_max, 10)
            curves.append((label, x, np.full_like(x, value)))

    fn_plot.plot_multi(st, curves, log, mat_class, param_name, unit_in, unit_out)


def param_check(parsed):
    '''All selections must share the same parameter to be comparable.'''
    params = [p['parameter'] for p in parsed]
    if any(p != params[0] for p in params):
        st.warning('Please select data with the same parameter to compare')
        return False
    return True
