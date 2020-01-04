#!python3

import argparse
import copy
import sys

import dash_bio
import numpy as np
import pandas as pd
import plotly.graph_objs as go
# app
from dash import callback_context
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate

# helpers
import helpers


def main(filename, mode, soap_cutoff_radius=4.5, marker_radius=1.0, config_filename=None, title='Example',
         height_viewer=500, width_viewer=500):
    # read the data for the first time
    initial_data = dict()

    # either from config or the args
    if config_filename is not None and config_filename != 'None':
        initial_data.update(helpers.parse_config(config_filename))
    else:
        initial_data['styles'] = helpers.get_style_config_dict(title, height_viewer, width_viewer)
        initial_data['soap_cutoff_radius'] = soap_cutoff_radius
        initial_data['marker_radius'] = marker_radius

    # update with the xyz data
    if 'extended_xyz_file' in initial_data.keys():
        initial_data.update(helpers.load_xyz(initial_data['extended_xyz_file'], initial_data['mode']))
    else:
        initial_data.update(helpers.load_xyz(filename, mode))

    # set up the application
    app = helpers.initialise_application(initial_data)

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
    def update_graph(data, x_axis_key, y_axis_key, marker_size_key, marker_colour_key, marker_size_range,
                     marker_size_limits, marker_colour_limits, marker_opacity_value, colourscale_name):

        # hack it out from there for now
        dataframe = pd.read_json(data['df_json'])

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
        marker_opacity_value = helpers.process_marker_opacity_value(marker_opacity_value)

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
                    size_new[idx] = helpers.get_new_sizes(size_new_i, [size_new_lower, size_new_upper],
                                                          marker_size_range)
        except:
            print('Error in scaling marker sizes. Using `30` for all data points instead.')
            size_new = np.asarray([30] * len(size_new))

        graph_data = {
            'data': [go.Scatter(
                x=dataframe[dataframe.columns.tolist()[x_axis_key]].tolist(),
                y=dataframe[dataframe.columns.tolist()[y_axis_key]].tolist(),
                mode='markers',
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
                                       'title': dataframe.columns.tolist()[y_axis_key]}
                                )
        }

        return graph_data

    @app.callback(Output('div-3dviewer', 'children'),
                  [Input('graph', 'clickData'),
                   Input('app-memory', 'data'),
                   Input('input_periodic_repetition_structure', 'value')])
    def update_3d_viewer_on_hover(hover_data_dict, data, periodic_repetition_str):
        """
        Update the visualiser on a hover event.
        If the event is None, then no change occurs.

        Note:
        Initialisation is handled by the change of data callback.

        :param hover_data_dict:
        :param data:
        :return:
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

        viewer_data = helpers.construct_3d_view_data(data, point_index, periodic_repetition_str)
        return dash_bio.Molecule3dViewer(**viewer_data)

    @app.callback([Output('dropdown-x-axis', 'options'),
                   Output('dropdown-y-axis', 'options'),
                   Output('dropdown-marker-size', 'options'),
                   Output('dropdown-marker-colour', 'options')],
                  [Input('app-memory', 'data')])
    def update_dropdown_options(data):
        """
        Change the contents of the dropdown menus to the dataframe columns.

        Need to call after init, but the data change is doing at_json actually

        :param data:
        :return:
        """

        options = [{'label': '{}'.format(l), 'value': i} for i, l in enumerate(pd.read_json(data['df_json']).columns)]

        return options, options, options, options

    # apparently in DEBUG=True mode, the main() is executed twice. I am not sure why. (tks32)
    app.run_server(debug=False, port=9999)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--fxyz', type=str, help='Location of xyz file')
    parser.add_argument('--config-file', type=str, default='None',
                        help='Config file that configures and overwrites every other argument')
    parser.add_argument('--width', type=int, default=600, help='Adjustment of graph width for small or large screens')
    parser.add_argument('--height', type=int, default=600, help='Adjustment of graph height for small or large screens')
    parser.add_argument('--mode', type=str, default='molecular',
                        help='Mode of projection ([molecular], [atomic]), "compound" coming soon')
    parser.add_argument('--title', type=str, default='Example', help='Titile of the plot')

    parser.add_argument('--marker-radius', type=float, default=1.0,
                        help='Radius of the green sphere, that in atomic mode allows you to identify '
                             'the current atom in the structure')
    parser.add_argument('--soap-cutoff', type=float, default=3.0,
                        help='Cutoff radius for wireframe of SOAP in atomic mode')

    # print help if no args were given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    sys.exit(main(filename=args.fxyz,
                  height_viewer=args.height,
                  width_viewer=args.width,
                  mode=args.mode,
                  title=args.title,
                  config_filename=args.config_file,
                  marker_radius=args.marker_radius,
                  soap_cutoff_radius=args.soap_cutoff))
