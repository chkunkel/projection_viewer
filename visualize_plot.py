#!python3

import argparse
import configparser
import json
import sys

import ase.io
import dash
import dash_bio
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objs as go

import helpers


def main(config_filename, extended_xyz_file, mode, title, soap_cutoff_radius, marker_radius, height_graph):
    if config_filename != 'None':
        # read config if given
        config = configparser.ConfigParser()
        config.read(config_filename)
        extended_xyz_file = config['Basic']['extended_xyz_file']
        mode = config['Basic']['mode']
        title = config['Basic']['title']
        soap_cutoff_radius = config['Basic']['soap_cutoff_radius']
        marker_radius = config['Basic']['marker_radius']
        height_graph = int(config['Basic']['height_graph'])

    # read atoms
    atoms = ase.io.read(extended_xyz_file, ':')
    [atoms[i].set_pbc(False) for i in range(len(atoms))]

    # Setup of the dataframes and atom/molecular infos for the 3D-Viewer
    shapes = []
    dataframe = helpers.build_dataframe_features(atoms, mode=mode)
    if mode == 'atomic':
        c_first_marker = atoms[0].get_positions()[0]
        system_ids = dataframe['system_ids']
        atomic_numbers = dataframe['atomic_numbers']
        dataframe.drop(['atomic_numbers', 'system_ids'], axis=1, inplace=True)

    print('New Dataframe\n', dataframe.head())

    # add a periodic box if needed
    shapes += helpers.get_periodic_box_shape_dict(atoms[0])

    # CONSTANT graph styles
    const_style_dropdown = {'height': '35px', 'width': '100%', 'display': 'inline-block'}
    const_style_colorscale = {'height': '25px', 'width': '100%', 'display': 'inline-block'}

    # Initial data and styles for the graph and 3D viewer
    viewer_3d_default_style = helpers.return_style(atoms[0], default=0)
    x_default = dataframe[dataframe.columns.tolist()[0]].tolist()
    y_default = dataframe[dataframe.columns.tolist()[1]].tolist()
    graph_marker_size_default = dataframe[dataframe.columns.tolist()[2]].tolist()
    graph_marker_size_default = np.array(graph_marker_size_default)
    graph_marker_size_default = list(graph_marker_size_default - min(graph_marker_size_default))  # cant be smaller than 0
    graph_color_default = dataframe[dataframe.columns.tolist()[3]].tolist()
    colorbar_title = dataframe.columns.tolist()[3]


    # Setup of app
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.Div(children=title, className='what-is', id='main_title'),

        html.Div([
            html.Span(["x-axis", html.Br(),
                       dcc.Dropdown(
                           id='x-axis',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=0, style=const_style_dropdown)], className='app__dropdown',
                      style={'width': '25%', 'display': 'inline-block'}),
            html.Span(['y-axis',
                       dcc.Dropdown(
                           id='y-axis',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=1, style=const_style_dropdown)], className='app__dropdown',
                      style={'width': '25%', 'display': 'inline-block'}),
            html.Span(["marker-size",
                       dcc.Dropdown(
                           id='marker_size',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=2, style=const_style_dropdown)], className='app__dropdown',
                      style={'width': '25%', 'display': 'inline-block'}),
            html.Span(["marker-color",
                       dcc.Dropdown(
                           id='marker_color',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=3, style=const_style_dropdown)], className='app__dropdown',
                      style={'width': '25%', 'display': 'inline-block'}),
        ], className="app__dropdown"),

        html.Div([
            html.Span([html.I('colorscale'), html.Br(),
                       dcc.Input(
                           id='colorscale',
                           type='text',
                           placeholder='colorscale',
                           style=const_style_colorscale)], className='app__dropdown',
                      style={'width': '15%', 'display': 'inline-block'}),
        ], className='app__input', style={'width': '15%', 'display': 'inline-block'}),
        html.Div([
            html.Span(["marker-size-limits",
                       dcc.RangeSlider(
                           id='marker_size_limits',
                           min=1, max=100, step=0.1, value=[5, 50],
                           marks={s: s for s in range(0, 101, 10)},
                           allowCross=False,
                       )], className='app__slider', style={'width': '50%', 'display': 'inline-block'}),
            html.Br(),
            html.Br(),
        ], className="app__slider"),
        html.Div([
            html.Span(["marker-color-limits",
                       dcc.RangeSlider(
                           id='marker_color_limits',
                           min=0, max=100, step=0.1, value=[0, 100],
                           marks={p: '{}%'.format(p) for p in range(0, 101, 10)},
                           allowCross=False,
                       )], className='app__slider', style={'width': '50%', 'display': 'inline-block'}),
            html.Br(),
            html.Br(),
        ], className="app__slider"),

        html.Div([
            dcc.Graph(
                id='graph',
                hoverData={},
                figure={
                    'data': [
                        {'x': x_default,
                         'y': y_default,
                         'mode': 'markers',
                         'marker': {
                             'color': graph_color_default,
                             'colorscale': "Viridis",
                             'colorbar': {'title': colorbar_title},
                             'size': graph_marker_size_default,
                             'line': {
                                 'color': 'rgb(0, 116, 217)',  # todo: implement border color option
                                 'width': 0.5
                             }, },

                         'name': 'TODO'},
                    ],
                    'layout': {
                        'xaxis': {'zeroline': False},
                        'yaxis': {'zeroline': False},
                        # 'title': 'Data Visualization',
                        'height': height_graph,
                    }
                }
            )
        ], style={'width': '63%', 'display': 'inline-block'}),

        html.Div([dcc.Loading(html.Div([
            dash_bio.Molecule3dViewer(
                id='3d-viewer',
                styles=viewer_3d_default_style,
                shapes=shapes,
                modelData=json.loads(helpers.ase2json(atoms[0]))),
            html.Div(id='molecule3d-output')
        ],
            id='div-3dviewer'))], className='container bg-white p-0',
            style={'vertical-align': 'center', 'width': '35.5%', 'display':
                'inline-block', 'border-style': 'solid', 'height': height_graph}),
        'Remarks:', html.Br(),
        'Gray wireframe: SOAP cutoff radius around selected atom.', html.Br(),
        'Green sphere: Marker for selected atom.'
    ],
        className='app-body')

    # Callbacks that update the viewer

    @app.callback(
        dash.dependencies.Output('graph', 'figure'),
        [dash.dependencies.Input('x-axis', 'value'),
         dash.dependencies.Input('y-axis', 'value'),
         dash.dependencies.Input('marker_size', 'value'),
         dash.dependencies.Input('marker_size_limits', 'value'),
         dash.dependencies.Input('marker_color', 'value'),
         dash.dependencies.Input('marker_color_limits', 'value'),
         dash.dependencies.Input('colorscale', 'value')])
    def update_graph(x_axis, y_axis, marker_size, marker_size_limits, marker_color, marker_color_limits, colorscale):
        color_new = dataframe[dataframe.columns.tolist()[marker_color]]
        color_span = np.abs(np.max(color_new) - np.min(color_new))
        color_new_lower = np.min(color_new) + color_span / 100. * marker_color_limits[0]
        color_new_upper = np.min(color_new) + color_span / 100. * marker_color_limits[1]
        indices_in_limits = np.asarray(
            [idx for idx, val in enumerate(color_new) if color_new_lower <= val <= color_new_upper])

        size_new = dataframe[dataframe.columns.tolist()[marker_size]].tolist()
        size_new = np.array(size_new)
        size_new = size_new - min(size_new)  # cant be smaller than 0
        try:
            size_new = _get_new_sizes(size_new, marker_size_limits)
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

        return {'data': [go.Scatter(
            x=dataframe[dataframe.columns.tolist()[x_axis]].tolist(),
            y=dataframe[dataframe.columns.tolist()[y_axis]].tolist(),
            mode='markers',
            marker={
                'color': color_new,
                'colorscale': 'Viridis' if colorscale is None or colorscale == '' else colorscale,
                'size': size_new,
                'colorbar': {'title': dataframe.columns.tolist()[marker_color]},
                'line': {
                    'color': 'rgb(0, 116, 217)',
                    'width': 0.5
                }},

            name='TODO',
        )],
            'layout': go.Layout(height=height_graph,
                                #         title = 'Data Visualization'
                                xaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside',
                                       'showline': True, 'mirror': True, 'title': dataframe.columns.tolist()[x_axis]},
                                yaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside',
                                       'showline': True, 'mirror': True, 'title': dataframe.columns.tolist()[y_axis]}
                                )
        }

    def _get_new_sizes(ref_values, size_range):
        """Map ``ref_values`` to a range within ``size_range`` in a linear fashion."""
        ref_values = np.asarray(ref_values)
        ref_min, ref_max = np.min(ref_values), np.max(ref_values)
        slope = (size_range[1] - size_range[0]) / float(ref_max - ref_min)
        return size_range[0] + slope * (ref_values - ref_min)

    def return_modelData_atoms(callback_hoverdict):
        atoms_id = callback_hoverdict["points"][0]["pointNumber"]
        if mode == "atomic":
            atoms_id = system_ids[atoms_id]
        return json.loads(helpers.ase2json(atoms[atoms_id]))

    def return_style_callback(callback_hoverdict, default=-1):
        atoms_id = callback_hoverdict["points"][0]["pointNumber"]
        if mode == "atomic":
            atoms_id = system_ids[atoms_id]
        if default == -1:
            atoms_id = atoms[atoms_id]
        else:
            atoms_id = atoms[default]
        return helpers.return_style(atoms_id, default=-1)

    def return_shape_callback(callback_hoverdict, default=-1):
        atoms_id = callback_hoverdict["points"][0]["pointNumber"]
        callback_id = callback_hoverdict["points"][0]["pointNumber"]
        if mode == "atomic":
            atoms_id = system_ids[atoms_id]
        if default == -1:
            atoms_id = atoms[atoms_id]
        else:
            atoms_id = atoms[default]

        shapes = []
        if mode == 'atomic':
            # displaced by CoM as well as the whole viewer
            pos = atoms_id.get_positions()[atomic_numbers[callback_id]] - atoms_id.get_center_of_mass()
            print(atoms_id, atomic_numbers[callback_id], pos)
            print(callback_id, atomic_numbers[callback_id])
            shapes = [{'type': 'Sphere', "color": "gray",
                       "center": {'x': pos[0], 'y': pos[1], 'z': pos[2]},
                       "radius": soap_cutoff_radius, 'wireframe': True},
                      {'type': 'Sphere', "color": "green",
                       "center": {'x': pos[0], 'y': pos[1], 'z': pos[2]},
                       "radius": marker_radius}
                      ]
        shapes += helpers.get_periodic_box_shape_dict(atoms_id)
        return shapes

    @app.callback(
        dash.dependencies.Output('div-3dviewer', 'children'),
        [dash.dependencies.Input('graph', 'clickData')])
    def update_3dviewer(callback_hoverdict, default=-1):
        print(callback_hoverdict)

        shapes = return_shape_callback(callback_hoverdict)
        styles = return_style_callback(callback_hoverdict)
        modelData = return_modelData_atoms(callback_hoverdict)

        view = dash_bio.Molecule3dViewer(
            styles=styles,
            shapes=shapes,
            modelData=modelData)
        return view

    app.run_server(debug=False, port=9999)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--fxyz', type=str, help='Location of xyz file')
    parser.add_argument('--config-file', type=str, default='None',
                        help='Config file that configures and overwrites every other argument')
    parser.add_argument('--height', type=int, default=530, help='Adjustment of graph height for small or large screens')
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

    sys.exit(main(extended_xyz_file=args.fxyz,
                  height_graph=args.height,
                  mode=args.mode,
                  title=args.title,
                  config_filename=args.config_file,
                  marker_radius=args.marker_radius,
                  soap_cutoff_radius=args.soap_cutoff))
