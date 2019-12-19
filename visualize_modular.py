#!python3

import sys

import ase.io
import dash_bio
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
# app
from dash import Dash, callback_context
from dash.dependencies import Output, Input

# helpers
import helpers


def initialise_application(data):
    """
    Set up the application. This should be ran only once, at the beginning of the session.

    :return:
    """

    # STYLE SETTINGS
    const_style_dropdown = {'height': '35px', 'width': '100%', 'display': 'inline-block'}
    const_style_colorscale = {'height': '25px', 'width': '100%', 'display': 'inline-block'}

    markdown_text = """**Green sphere:** Selected atom marker.  &nbsp;&nbsp;**Gray wireframe:** SOAP cutoff radius. 
    **Mouse-Navigation:**  &nbsp;*Mouse:* Rotate,  &nbsp;&nbsp;*Ctrl+Mouse:* Translate,  &nbsp;&nbsp;*Shift+Mouse:* 
    Zoom """

    # Setup of app
    app = Dash(__name__)

    # TODO: callbacks
    #  1. dropdown menu content updates
    #     REMOVED, need to update:
    #     [{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)]
    #  2. initialisation of the graph
    #  3. initialisation of the 3d viewer
    #       - viewer_3d_default_style = helpers.return_style(atoms[0], default=0)
    #       - dash_bio.Molecule3dViewer(
    #             id='3d-viewer',
    #             styles=viewer_3d_default_style,
    #             shapes=shapes,
    #             modelData=json.loads(helpers.ase2json(atoms[0])))

    # todo: rename height_graph and width_graph to viewer_<...> because it is the viewer's setting

    # layout
    app.layout = html.Div(className='app-body',
                          children=[
                              # storage of the data in the application
                              dcc.Store(id='app-memory', data=data),

                              # title of the visualiser
                              html.H3(children=data['styles']['title']),

                              # Controls: Dropdown menus, opacity and choice of colourscale
                              html.Div(className="app__controls", children=[
                                  # dropdown menu for the x-axis
                                  html.Span(className='app__dropdown',
                                            children=["x-axis", html.Br(),
                                                      dcc.Dropdown(id='dropdown-x-axis', style=const_style_dropdown,
                                                                   options=[], value=0)]),
                                  # dropdown menu for the y-axis
                                  html.Span(className='app__dropdown',
                                            children=["y-axis", html.Br(),
                                                      dcc.Dropdown(id='dropdown-y-axis', style=const_style_dropdown,
                                                                   options=[], value=0)]),
                                  # dropdown menu for the marker size
                                  html.Span(className='app__dropdown',
                                            children=["marker size", html.Br(),
                                                      dcc.Dropdown(id='dropdown-marker-size',
                                                                   style=const_style_dropdown, options=[], value=0)]),
                                  # dropdown menu for the marker colour
                                  html.Span(className='app__dropdown',
                                            children=["marker colour", html.Br(),
                                                      dcc.Dropdown(id='dropdown-marker-colour',
                                                                   style=const_style_dropdown, options=[], value=0)]),
                                  # input field for marker opacity
                                  html.Span(className='app__input',
                                            children=['marker opacity', html.Br(),
                                                      dcc.Input(
                                                          id='input-marker-opacity',
                                                          type='text',
                                                          placeholder='marker opacity 0.0 - 1.0')]),
                                  # input field for colourscale
                                  html.Span(className='app__input',
                                            children=['colourscale name', html.Br(),
                                                      dcc.Input(
                                                          id='input-colourscale',
                                                          type='text',
                                                          placeholder='colourscale')])
                              ]),

                              # Controls: Sliders for colour and size limits
                              html.Div(className='app__controls', children=[
                                  # Slider: marker size limits s
                                  html.Span(className='app__slider',
                                            children=['marker size limits',
                                                      dcc.RangeSlider(id='slider_marker_size_limits', min=1, max=100,
                                                                      step=0.1, value=[5, 50],
                                                                      marks={s: str(s) for s in range(0, 101, 10)},
                                                                      allowCross=False)]),

                                  html.Span(className='app__slider',
                                            children=["marker colour limits",
                                                      dcc.RangeSlider(id='slider_marker_color_limits', min=0, max=100,
                                                                      step=0.1, value=[0, 100],
                                                                      marks={p: '{}%'.format(p) for p in
                                                                             range(0, 101, 10)},
                                                                      allowCross=False, )],
                                            ),
                                  # two of Br, perhaps we can remove these?
                                  html.Br(),
                                  html.Br(),
                              ]),

                              # Graph: placeholder, filled on graph intialisation
                              html.Div(className='app__container_scatter', children=[
                                  dcc.Graph(id='graph', figure={'data': [], 'layout': {}})], ),

                              # 3D Viewer
                              # a main Div, with a dcc.Loading compontnt in it for loading of the viewer
                              html.Div(className='app__container_3dmolviewer',
                                       style={'height': data['styles']['height_viewer'],
                                              'width_graph': data['styles']['width_viewer']},
                                       children=[
                                           # loading component for the 3d viewer
                                           dcc.Loading(
                                               html.Div(children=[
                                                   html.Div(id='div-3dviewer',
                                                            # the actual viewer will be initialised here
                                                            # todo: check that at_json works
                                                            children=[]),
                                                   # some info at the bottom of the viewer
                                                   dcc.Markdown(id='markdown-info-in-viewer',
                                                                children=markdown_text,
                                                                className='app__remarks_viewer')
                                               ]))])])

    return app


def load_xyz(filename, mode='atomic', verbose=True):
    """
    Loads the XYZ file

    :param filename:
    :param mode:
    :param verbose:
    :return:
    """

    # read atoms
    atoms_list = ase.io.read(filename, ':')
    [atoms_list[i].set_pbc(False) for i in range(len(atoms_list))]

    # Setup of the dataframes and atom/molecular infos for the 3D-Viewer
    df = helpers.build_dataframe_features(atoms_list, mode=mode)
    system_index = None
    atom_index_in_systems = None
    if mode == 'atomic':
        system_index = df['system_ids']
        atom_index_in_systems = df['atomic_numbers']
        df.drop(['atomic_numbers', 'system_ids'], axis=1, inplace=True)

    if verbose:
        print('New Dataframe\n', df.head())

    at_list_json = [helpers.ase2json(at) for at in atoms_list]

    data = {'system_index': system_index,
            'atom_index_in_systems': atom_index_in_systems,
            'df_json': df.to_json(),
            'atoms_list_json': at_list_json,
            'mode': mode}

    return data


def get_style_config_dict(title='Example', height_viewer=500, width_viewer=500, **kwargs):
    config_dict = dict(title=title,
                       height_viewer=height_viewer,
                       height_graph=height_viewer,
                       width_viewer=width_viewer,
                       width_graph=width_viewer,
                       **kwargs)

    return config_dict


def main(filename, mode, soap_cutoff_radius=4.5, marker_radius=1.0):
    # read the data for the first time
    initial_data = dict()

    # update with the xyz data
    initial_data.update(load_xyz(filename, mode))
    initial_data['styles'] = get_style_config_dict('f', 500, 500)  # todo: add title and such stuff here
    initial_data['soap_cutoff_radius'] = soap_cutoff_radius
    initial_data['marker_radius'] = marker_radius

    # set up the application
    app = initialise_application(initial_data)

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

        ctx = callback_context

        print('DEBUG CTX {}'.format(ctx.__dict__))

        # if hover_data_dict is None:
        #     raise PreventUpdate

        print('DEBUG update 3d viewer with dict: \n\t{}'.format(hover_data_dict))

        try:
            point_index = hover_data_dict['pointNumber']
        except TypeError:
            point_index = 0

        viewer_data = helpers.construct_3d_view_data(data, point_index)

        return dash_bio.Molecule3dViewer(**viewer_data)

    # @app.callback(Output('div-3dviewer', 'children'),
    #               [Input('app-memory', 'data')])
    # def update_3d_viewer_on_data_update(data):
    #     """
    #     Update the viewer when data change event occurs.
    #     This time, the 0th configuration is visualised, with no soap sphere.
    #
    #     :param data:
    #     :return:
    #     """
    #     print('DEBUG update 3d viewer on data update')
    #
    #     point_index = 0
    #     viewer_data = helpers.construct_3d_view_data(data, point_index, skip_soap=True)
    #
    #     return dash_bio.Molecule3dViewer(**viewer_data)

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

    app.run_server(debug=True, port=9999)


if __name__ == "__main__":
    # parse arguments

    sys.exit(main('ASAP-pca-d4-new.xyz', 'atomic'))
