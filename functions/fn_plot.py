import numpy as np
import pandas as pd
import altair as alt

# Plots are rendered with Altair (vega-lite): the browser draws the chart
# client-side, so reruns only ship a small JSON spec instead of a
# server-rendered matplotlib PNG. This is the main reason the UI feels
# instant compared to the original app.

LINE_COLOR = '#FF0066'
CHART_HEIGHT = 420


def axis_config(mat_class, param_name, unit_in, unit_out):
    '''Reproduce the original axis-label/limit rules.'''
    xlabel = '[' + str(unit_in) + ']'
    ylabel = str(param_name) + '  [' + str(unit_out) + ']'
    ydomain = None

    if param_name == 'half cell ocv':
        ylabel = 'voltage [V]'
        xlabel = 'degree of lithiation θ'
        ydomain = (3, 4.5) if mat_class == 'positive' else (0, 2)

    if param_name == 'diffusion coefficient' and mat_class != 'electrolyte':
        xlabel = 'degree of lithiation θ'

    if mat_class == 'electrolyte':
        xlabel = 'concentration [mol·m⁻³]'
        if param_name == 'ionic conductivity':
            ydomain = (0, 1.6)

    return xlabel, ylabel, ydomain


def _make_chart(df, log, xlabel, ylabel, ydomain, color_field=None, color=None):
    if log == 'log':
        # log axes cannot show non-positive values; drop them up front so
        # vega-lite doesn't silently produce an empty chart
        df = df[df['y'] > 0]
        yscale = alt.Scale(type='log')
    elif ydomain is not None:
        yscale = alt.Scale(domain=list(ydomain))
    else:
        yscale = alt.Scale(zero=False)

    tooltip = [alt.Tooltip('x', format='.4g', title=xlabel),
               alt.Tooltip('y', format='.4g', title=ylabel)]
    encodings = dict(
        x=alt.X('x', title=xlabel),
        y=alt.Y('y', title=ylabel, scale=yscale),
        # draw points in data order (like matplotlib), not sorted by x —
        # matters for non-monotonic curves such as hysteresis loops
        order=alt.Order('idx'),
    )
    if color_field:
        encodings['color'] = alt.Color(color_field, title=None,
                                       legend=alt.Legend(orient='bottom', columns=2, labelLimit=400))
        tooltip.append(alt.Tooltip(color_field, title='source'))
    encodings['tooltip'] = tooltip

    points = bool(len(df) <= 3)  # show markers when there are barely any points
    mark_kwargs = dict(clip=True, point=points, strokeWidth=2)
    if color:
        mark_kwargs['color'] = color
    chart = (alt.Chart(df)
             .mark_line(**mark_kwargs)
             .encode(**encodings)
             .properties(height=CHART_HEIGHT)
             .interactive())
    return chart


def plot_single(container, x, y, log, mat_class, param_name, unit_in, unit_out):
    '''Plot one parameter curve into the given streamlit container.'''
    xlabel, ylabel, ydomain = axis_config(mat_class, param_name, unit_in, unit_out)
    df = pd.DataFrame({'x': np.asarray(x, dtype=float),
                       'y': np.asarray(y, dtype=float)}).dropna()
    df['idx'] = range(len(df))
    chart = _make_chart(df, log, xlabel, ylabel, ydomain, color=LINE_COLOR)
    container.altair_chart(chart, use_container_width=True)


def plot_multi(container, curves, log, mat_class, param_name, unit_in, unit_out):
    '''Plot several curves for comparison. `curves` is a list of
    (label, x, y) tuples.'''
    xlabel, ylabel, ydomain = axis_config(mat_class, param_name, unit_in, unit_out)
    frames = []
    for label, x, y in curves:
        frame = pd.DataFrame({'x': np.asarray(x, dtype=float),
                              'y': np.asarray(y, dtype=float),
                              'source': str(label)}).dropna()
        frame['idx'] = range(len(frame))
        frames.append(frame)
    if not frames:
        container.caption('Nothing to plot')
        return
    df = pd.concat(frames, ignore_index=True)
    chart = _make_chart(df, log, xlabel, ylabel, ydomain, color_field='source')
    container.altair_chart(chart, use_container_width=True)
