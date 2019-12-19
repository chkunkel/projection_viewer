#!python3

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


def main(filename, mode, soap_cutoff_radius=4.5, marker_radius=1.0):
    # read the data for the first time
    initial_data = dict()

    # update with the xyz data
    initial_data.update(helpers.load_xyz(filename, mode))
    initial_data['styles'] = helpers.get_style_config_dict('f', 500, 500)  # todo: add title and such stuff here
    initial_data['soap_cutoff_radius'] = soap_cutoff_radius
    initial_data['marker_radius'] = marker_radius

    # set up the application
    app = helpers.initialise_application(initial_data)

    @app.callback(Output('graph', 'figure'),
                  [Input('app-memory', 'data'),
                   Input('dropdown-x-axis', 'value'),
                   Input('dropdown-y-axis', 'value'),
                   Input('dropdown-marker-size', 'value'),
                   Input('dropdown-marker-colour', 'value'),
                   Input('slider_marker_size_limits', 'value'),
                   Input('slider_marker_color_limits', 'value'),
                   Input('input-marker-opacity', 'value'),
                   Input('input-colourscale', 'value')])
    def update_graph(data, x_axis_key, y_axis_key, marker_size_key, marker_colour_key, marker_size_limits,
                     marker_colour_limits, marker_opacity_value, colourscale_name):

        # hack it out from there for now
        dataframe = pd.read_json(data['df_json'])

        color_new = dataframe[dataframe.columns.tolist()[marker_colour_key]]
        color_span = np.abs(np.max(color_new) - np.min(color_new))
        color_new_lower = np.min(color_new) + color_span / 100. * marker_colour_limits[0]
        color_new_upper = np.min(color_new) + color_span / 100. * marker_colour_limits[1]
        indices_in_limits = np.asarray(
            [idx for idx, val in enumerate(color_new) if color_new_lower <= val <= color_new_upper])

        size_new = dataframe[dataframe.columns.tolist()[marker_size_key]].tolist()
        size_new = np.array(size_new)
        size_new = size_new - min(size_new)  # cant be smaller than 0

        # marker opacity value to float
        marker_opacity_value = helpers.process_marker_opacity_value(marker_opacity_value)

        try:
            size_new = helpers._get_new_sizes(size_new, marker_size_limits)
        except:
            print('Error in scaling marker sizes. Using `30` for all data points instead.')
            size_new = np.asarray([30] * len(size_new))
        size_new_tmp = []
        for idx, size_i in enumerate(size_new):
            if idx in indices_in_limits:
                size_new_tmp.append(size_i)
            else:
                size_new_tmp.append(0)
        size_new = np.asarray(size_new_tmp)

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
                    'line': {
                        'color': 'rgb(0, 116, 217)',
                        'width': 0.5
                    }},

                name='TODO',
            )],
            'layout': go.Layout(height=data['styles']['height_graph'],
                                hovermode='closest',
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
                   Input('app-memory', 'data')])
    def update_3d_viewer_on_hover(hover_data_dict, data):
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
        if ctx.triggered:
            if ctx.triggered[0]['prop_id'].split('.')[0] == 'app-memory':
                point_index = 0
            elif ctx.triggered[0]['prop_id'].split('.')[0] == 'graph':
                if hover_data_dict is None:
                    raise PreventUpdate

                print('DEBUG update 3d viewer with dict: \n\t{}'.format(hover_data_dict))
                try:
                    point_index = hover_data_dict['pointNumber']
                except TypeError:
                    point_index = 0
        else:
            print('DEBUG: update of 3d viewer prevented by callback_context.triggered=False')
            raise PreventUpdate

        viewer_data = helpers.construct_3d_view_data(data, point_index)

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

    sys.exit(main('ASAP-pca-d4-new.xyz', 'atomic'))
