import copy
import subprocess
import sys
import traceback

import dash_bio
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash import callback_context
from dash.exceptions import PreventUpdate

from projection_viewer import processors
from projection_viewer import utils
from projection_viewer.frontend import visualiser


def show_summary(click, q_val, p_val):
    """

    Default callback
    @app.callback(Output('markdown_output', 'children'),
              [Input('button_summary', 'n_clicks')],
              [State('abcd_query_input_box', 'value'),
               State('abcd_prop_input_box', 'value')])

    """
    print('DEBUG: called show_summary() with args \n {}'.format((click, q_val, p_val)))

    if click is None:
        print('PreventUpdate in show_summary()')
        raise PreventUpdate

    if isinstance(q_val, str):
        q_val = q_val.replace('\n', ' ')
        q_val = q_val.replace('"', '\\"')
        if q_val.strip() == '':
            q_val = None

    if isinstance(p_val, str):
        p_val = p_val.replace('\n', ' ')
        p_val = p_val.replace('"', '\\"')
        if p_val.strip() == '':
            p_val = None

    print('DEBUG: args changed to  \n {}'.format((click, q_val, p_val)))

    try:
        # noinspection PyUnresolvedReferences
        run = get_ipython().getoutput
        ipy_runner = True
    except NameError:
        def run(cmd):
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            result = result.stdout.decode('utf-8')
            return result.split('\n')

        ipy_runner = False

    # define command as needed
    if ipy_runner:
        abcd_cmd = 'abcd summary '
        if p_val is not None:
            abcd_cmd += ' -p "{}"'.format(p_val)
        if q_val is not None:
            abcd_cmd += ' -q "{}"'.format(q_val)

    else:
        abcd_cmd = ['abcd', 'summary']
        if p_val is not None:
            abcd_cmd += ['-p', p_val]
        if q_val is not None:
            abcd_cmd += ['-q', q_val]

    # get the output
    print('\n\nDEBUG: abcd command:\n>>>{}'.format(abcd_cmd))
    abcd_out = run(abcd_cmd)

    try:
        if '...' in abcd_out[-1]:
            if ipy_runner:
                abcd_out = run(abcd_cmd + ' --all')
            else:
                abcd_out = run(abcd_cmd + [' --all'])
    except IndexError:
        pass

    print('DEBUG: output of abcd is {}'.format(abcd_out))

    md_output = '```\n{}\n```'.format('\n'.join(abcd_out))

    return md_output


def update_all_data_on_new_query(n_clicks, q_value, p_value, data_originally):
    """
    Updates the data of the viewer as a result of a new ABCD query.

    Note:
    Takes time and computation, so need to be optimised and ran the minimal number of times.

    Default decorator:
    @app.callback(Output('app-memory', 'data'),
                [Input('button_visualise', 'n_clicks')],
                [State('abcd_query_input_box', 'value'),
                 State('abcd_prop_input_box', 'value'),
                 State('app-memory', 'data')])
    """

    print('CALLBACK update_all_data_on_new_query() beginning\nkeys in data:{}'.format(data_originally.keys()))

    if n_clicks is None:
        # this is the initial call, on construction of the button
        return data_originally
    else:
        if q_value is None:
            print('DEBUG: update_all_data_on_new_query(): PreventUpdate due to None in query')
            raise PreventUpdate

    print('\n\n\n\nRunning ABCD query of `{}` with n_clicks `{}`'.format(q_value, n_clicks))

    # run the ABCD query
    try:
        new_fn = processors.asap.abcd_exec_query_and_run_asap(q_value)
        new_data = utils.load_xyz(new_fn, data_originally['mode'])
        data_originally.update(new_data)
    except KeyboardInterrupt:
        # handle keyboard interrupt
        print('KeyboardInterrupt in update_all_data_on_new_query()')
        raise PreventUpdate

    except Exception as e:
        traceback.print_exc()
        sys.stderr.write('update_all_data_on_new_query' + ": " + repr(e) + "\n")
        raise PreventUpdate

    print('DEBUG data keys and stuff\nnew keys:{}\nresultant keys:{}\n\n\n\n'.format(new_data.keys(),
                                                                                     data_originally.keys()))
    print('CALLBACK update_all_data_on_new_query() end\nkeys in data:{}'.format(data_originally.keys()))
    return data_originally


################################################
# callbacks form the plder visualiser
################################################

def update_graph(data, x_axis_key, y_axis_key, marker_size_key, marker_colour_key, marker_size_range,
                 marker_size_limits, marker_colour_limits, marker_opacity_value, colourscale_name):
    """

    Default decorator:
    @app.callback(Output('graph', 'figure'),
              [Input('app-memory', 'data'),
               Input('dropdown-x-axis', 'value'),
               Input('dropdown-y-axis', 'value'),
               Input('dropdown-marker-size', 'value'),
               Input('dropdown-marker-colour', 'value'),
               Input('slider_marker_size_range', 'value'),
               Input('slider_marker_size_limits', 'value'),
               Input('slider_marker_color_limits', 'value'),
               Input('input-marker-opacity', 'value'),
               Input('input-colourscale', 'value')])

    """

    # hack it out from there for now
    try:
        dataframe = pd.read_json(data['df_json'])
    except KeyError:
        print('DEBUG, PreventUpdate; Key Error in update_graph:\nkeys:\n    {}'.format(data.keys()))
        raise PreventUpdate

    # todo: add context action to decide what to update if too slow

    # color limits
    color_new = copy.copy(dataframe[dataframe.columns.tolist()[marker_colour_key]])
    color_span = np.abs(np.max(color_new) - np.min(color_new))
    color_new_min = np.min(color_new)
    color_new_lower = color_new_min + color_span / 100. * marker_colour_limits[0]
    color_new_upper = color_new_min + color_span / 100. * marker_colour_limits[1]
    # indices_in_limits = np.asarray(
    #     [idx for idx, val in enumerate(color_new) if color_new_lower <= val <= color_new_upper])

    # marker opacity value to float
    marker_opacity_value = utils.process_marker_opacity_value(marker_opacity_value)

    # marker size
    size_new = copy.copy(dataframe[dataframe.columns.tolist()[marker_size_key]].tolist())  # fixme this is messy
    size_new = np.array(size_new)
    size_new = size_new - np.min(size_new)  # cant be smaller than 0
    size_new_range = np.max(size_new)
    size_new_lower = size_new_range / 100. * marker_size_limits[0]
    size_new_upper = size_new_range / 100. * marker_size_limits[1]

    try:
        # setting linear scale between the limits and flat below and above
        for idx, size_new_i in enumerate(size_new):
            if size_new_i < size_new_lower:
                size_new[idx] = marker_size_range[0]
            elif size_new_i > size_new_upper:
                size_new[idx] = marker_size_range[1]
            else:
                size_new[idx] = utils.get_new_sizes(size_new_i, [size_new_lower, size_new_upper],
                                                    marker_size_range)
    except:
        print('Error in scaling marker sizes. Using `30` for all data points instead.')
        size_new = np.asarray([30] * len(size_new))

    try:
        list_hovertexts = data['list_hovertexts']
    except KeyError:
        list_hovertexts = []

    graph_data = {
        'data': [go.Scatter(
            x=dataframe[dataframe.columns.tolist()[x_axis_key]].tolist(),
            y=dataframe[dataframe.columns.tolist()[y_axis_key]].tolist(),
            mode='markers',
            hovertext=list_hovertexts,
            marker={
                'color': color_new,
                'colorscale': 'Viridis' if colourscale_name is None or colourscale_name == '' else colourscale_name,
                'size': size_new,
                'colorbar': {'title': dataframe.columns.tolist()[marker_colour_key]},
                'opacity': marker_opacity_value,
                'cmin': color_new_lower,
                'cmax': color_new_upper,
                'line': {
                    'color': 'rgb(0, 116, 217)',
                    'width': 0.5
                }},

            name='TODO',
        )],
        'layout': go.Layout(hovermode='closest',
                            #         title = 'Data Visualization'
                            xaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside', 'automargin': True,
                                   'showline': True, 'mirror': True,
                                   'title': dataframe.columns.tolist()[x_axis_key]},
                            yaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside', 'automargin': True,
                                   'showline': True, 'mirror': True,
                                   'title': dataframe.columns.tolist()[y_axis_key]},
                            height=data['styles']['height_graph'],
                            )
    }

    return graph_data


def update_3d_viewer_on_hover(hover_data_dict, data, periodic_repetition_str):
    """
    Update the visualiser on a hover event.
    If the event is None, then no change occurs.

    Note:
    Initialisation is handled by the change of data callback.

    Default decorator:
    @app.callback(Output('div-3dviewer', 'children'),
              [Input('graph', 'clickData'),
               Input('app-memory', 'data'),
               Input('input_periodic_repetition_structure', 'value')])


    :param hover_data_dict:
    :param data:
    :param periodic_repetition_str:
    :return:

    Args:
        periodic_repetition_str:
        periodic_repetition_str:
    """

    # decide which one triggered the event
    ctx = callback_context
    point_index = 0
    if ctx.triggered:
        triggr_obj_name = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggr_obj_name == 'app-memory':
            pass
        elif triggr_obj_name == 'graph':
            if hover_data_dict is None:
                raise PreventUpdate

            print('DEBUG update 3d viewer with dict: \n\t{}'.format(hover_data_dict))
            try:
                point_index = hover_data_dict['points'][0]['pointNumber']
            except TypeError:
                point_index = 0
    else:
        print('DEBUG: update of 3d viewer prevented by callback_context.triggered=False')
        raise PreventUpdate

    # The visualiseable atoms do not exist on the initial call, so just an empty 3D viewer is enough
    try:
        viewer_data = visualiser.construct_3d_view_data(data, point_index,
                                                        periodic_repetition_str)
    except KeyError:
        viewer_data = dict()

    # noinspection PyUnresolvedReferences
    return dash_bio.Molecule3dViewer(**viewer_data)


def update_dropdown_options(data):
    """
    Change the contents of the dropdown menus to the dataframe columns.

    Need to call after init, but the data change is doing at_json actually

    :param data:
    :return:


    Default decorator:
    @app.callback([Output('dropdown-x-axis', 'options'),
               Output('dropdown-y-axis', 'options'),
               Output('dropdown-marker-size', 'options'),
               Output('dropdown-marker-colour', 'options')],
              [Input('app-memory', 'data')])
    """

    print('CALLBACK update_dropdown_options()\nkeys in data:{}'.format(data.keys()))

    # no options if the dataframe does not exist yet
    try:
        options = [{'label': '{}'.format(l), 'value': i} for i, l in
                   enumerate(pd.read_json(data['df_json']).columns)]
    except KeyError:
        options = []

    return options, options, options, options
