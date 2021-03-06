import configparser

import dash_bio
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash

from projection_viewer.utils import get_asset_folder, str2bool


def initialise_application_with_abcd(data, assets_folder=get_asset_folder()):
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
    app = Dash(__name__, assets_folder=assets_folder)

    # layout
    # noinspection PyUnresolvedReferences
    app.layout = html.Div(className='app-body',
                          children=[
                              # storage of the data in the application
                              dcc.Store(id='app-memory', data=data, storage_type='session'),

                              # title of the visualiser
                              html.H3(children=data['styles']['title'], id='main_title'),

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
                                  html.Span(className='app__dropdown',
                                            children=['marker opacity', html.Br(),
                                                      dcc.Input(
                                                          id='input-marker-opacity',
                                                          type='text',
                                                          placeholder='marker opacity 0.0 - 1.0')]),
                                  # input field for colourscale
                                  html.Span(className='app__dropdown',
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
                                            children=['marker size range',
                                                      dcc.RangeSlider(id='slider_marker_size_range', min=1, max=100,
                                                                      step=0.1, value=[5, 50],
                                                                      marks={s: str(s) for s in range(0, 101, 10)},
                                                                      allowCross=False)]),
                                  # New slider for marker size limits
                                  html.Span(className='app__slider',
                                            children=["marker-size-limits",
                                                      dcc.RangeSlider(
                                                          id='slider_marker_size_limits',
                                                          min=0, max=100, step=0.1, value=[0, 100],
                                                          marks={p: '{}%'.format(p) for p in range(0, 101, 10)},
                                                          allowCross=False, )], ),
                                  # Slider: marker colour limits
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

                              # DEV: adding ABCD elements
                              html.Div(className="app__controls",
                                       children=[
                                           html.Span([html.I('ABCD query'),
                                                      html.Br(),
                                                      dcc.Input(id='abcd_query_input_box',
                                                                type='text',
                                                                placeholder='your query',
                                                                style=const_style_colorscale)],
                                                     className='app__dropdown1',
                                                     style={'width': '50%', 'display': 'inline-block'}),
                                           html.Span(style={'width': '5%', 'display': 'inline-block'}),
                                           html.Span([html.Button('Submit query', id='button_submit_query')],
                                                     style={'width': '15%', 'display': 'inline-block'})
                                       ]),

                              # Graph: placeholder, filled on graph intialisation
                              html.Div(className='app__container_scatter', children=[
                                  dcc.Graph(id='graph', figure={'data': [], 'layout': {}})], ),

                              # 3D Viewer
                              # a main Div, with a dcc.Loading componnt in it for loading of the viewer
                              html.Div(
                                  className='app__container_3dmolviewer',
                                  style={'height': data['styles']['height_viewer'],
                                         'width_graph': data['styles']['width_viewer']},
                                  children=[
                                      # some info about the viewer
                                      dcc.Markdown(markdown_text, className='app__remarks_viewer'),
                                      # Input field for the periodic images
                                      html.Span(className='app__remarks_viewer',  # fixme: missing style
                                                children=['Periodic repetition of structure: ',
                                                          dcc.Input(id='input_periodic_repetition_structure',
                                                                    type='text',
                                                                    placeholder='(0,1) (0,1) (0,1)')]),
                                      # loading component for the 3d viewer
                                      dcc.Loading(
                                          # a div to hold the viewer
                                          html.Div(id='div-3dviewer', children=[
                                              # the actual viewer will be initialised here
                                              dash_bio.Molecule3dViewer(id='3d-viewer', styles={}, shapes={},
                                                                        modelData={})
                                          ]))]),

                          ])

    return app


def initialise_application(data, assets_folder=get_asset_folder()):
    """
    Set up the application. This should be ran only once, at the beginning of the session.
    """

    # Setup of app
    app = Dash(__name__, assets_folder=assets_folder)

    # layout
    app.layout = get_tab_layout_visualiser(data, store=True)

    return app


def parse_config(config_filename):
    """
    Reads parameters form a config file.
    """

    data = {}
    config = configparser.ConfigParser()
    config.read(config_filename)
    data['extended_xyz_file'] = config['Basic']['extended_xyz_file']
    data['mode'] = config['Basic']['mode']
    data['soap_cutoff_radius'] = config['Basic']['soap_cutoff_radius']
    data['marker_radius'] = config['Basic']['marker_radius']

    data['styles'] = {}
    data['styles']['title'] = config['Basic']['title']

    data['styles']['height_graph'] = int(config['Basic']['height_graph'])
    data['styles']['width_graph'] = int(config['Basic']['width_graph'])

    # take height and width of the viewer with backward compatibility;
    # the layout might be over-defined like this though
    try:
        data['styles']['width_viewer'] = int(config['Basic']['width_viewer'])
    except KeyError:
        data['styles']['width_viewer'] = int(config['Basic']['width_graph'])

    try:
        data['styles']['width_viewer'] = int(config['Basic']['width_viewer'])
    except KeyError:
        data['styles']['width_viewer'] = int(config['Basic']['width_graph'])

    data['styles']['width_viewer'] = int(config['Basic']['height_graph'])
    data['styles']['webgl'] = str2bool(config['Basic']['webgl'])

    return data


# noinspection PyUnresolvedReferences
def get_tab_layout_visualiser(data, store=True):
    # STYLE SETTINGS
    # const_style_dropdown = {'height': '35px', 'width': '100%', 'display': 'inline-block'}
    const_style_dropdown = dict()
    markdown_text = """**Green sphere:** Selected atom marker.  &nbsp;&nbsp;**Gray wireframe:** SOAP cutoff radius. 
        **Mouse-Navigation:**  &nbsp;*Mouse:* Rotate,  &nbsp;&nbsp;*Ctrl+Mouse:* Translate,  &nbsp;&nbsp;*Shift+Mouse:* 
        Zoom """

    layout = html.Div(className='app-body',
                      children=[
                          # storage of the data in the application
                          dcc.Store(id='app-memory', data=data, storage_type='session') if store else None,

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
                              html.Span(className='app__dropdown',
                                        children=['marker opacity', html.Br(),
                                                  dcc.Input(
                                                      id='input-marker-opacity',
                                                      type='text',
                                                      placeholder='marker opacity 0.0 - 1.0')]),
                              # input field for colourscale
                              html.Span(className='app__dropdown',
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
                                        children=['marker size range',
                                                  dcc.RangeSlider(id='slider_marker_size_range', min=1, max=100,
                                                                  step=0.1, value=[5, 50],
                                                                  marks={s: str(s) for s in range(0, 101, 10)},
                                                                  allowCross=False)]),
                              # New slider for marker size limits
                              html.Span(className='app__slider',
                                        children=["marker-size-limits",
                                                  dcc.RangeSlider(
                                                      id='slider_marker_size_limits',
                                                      min=0, max=100, step=0.1, value=[0, 100],
                                                      marks={p: '{}%'.format(p) for p in range(0, 101, 10)},
                                                      allowCross=False, )], ),
                              # Slider: marker colour limits
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
                          html.Div(
                              className='app__container_3dmolviewer',
                              style={'height': data['styles']['height_viewer'],
                                     'width_graph': data['styles']['width_viewer']},
                              children=[
                                  # some info about the viewer
                                  dcc.Markdown(markdown_text, className='app__remarks_viewer'),
                                  # Input field for the periodic images
                                  html.Span(className='app__remarks_viewer',  # fixme: missing style
                                            children=['Periodic repetition of structure: ',
                                                      dcc.Input(id='input_periodic_repetition_structure',
                                                                type='text',
                                                                placeholder='(0,1) (0,1) (0,1)')]),
                                  # loading component for the 3d viewer
                                  dcc.Loading(
                                      # a div to hold the viewer
                                      html.Div(id='div-3dviewer', children=[
                                          # the actual viewer will be initialised here
                                          # noinspection PyUnresolvedReferences
                                          dash_bio.Molecule3dViewer(id='3d-viewer', styles={}, shapes={},
                                                                    modelData={})
                                      ]))])
                      ])

    return layout


def get_tab_layout_abcd_summary():
    layout = html.Div(className='app-body', children=[
        # ABCD: left side
        html.Div(className='class_container_abcd', children=[
            # Controls 1: q, visualise, download
            html.Div(className="class__abcd_controls",
                     children=[
                         # html.Span(children=[
                         html.Span([html.I('-q', className='class__abcd_i')]),
                         # separator,
                         dcc.Input(className="class__abcd_input_filed",
                                   id='abcd_query_input_box',
                                   type='text',
                                   placeholder='your query (only one supported yet)'),
                         html.Span(className="class__abcd_separator", style={'width': '5%', 'display': 'inline-block'}),
                         # ]),
                     ]),

            # Controls 2: p and summary
            html.Div(className="class__abcd_controls",
                     children=[
                         html.Span(children=[
                             html.Span([html.I('-p', className='class__abcd_i')]),
                             dcc.Input(className="class__abcd_input_filed",
                                       id='abcd_prop_input_box',
                                       type='text',
                                       placeholder='your properties (only one supported yet)', ),
                         ]),
                     ]),

            # Controls 3: buttons
            html.Div(className="class__abcd_controls", children=[
                html.Button(children='Visualise', id='button_visualise', className="class__abcd_button", ),
                html.Button(children='Download', id='button_download', className="class__abcd_button"),
                html.Button(children='Summary', id='button_summary', className="class__abcd_button", ),
            ]),

            # the Markdown output
            html.Div([dcc.Markdown('```\n Something \n ```', className='app__remarks_viewer',
                                   id='markdown_output')])
        ]),
        # ASAP: right side
        html.Div(className='class_container_asap', children=[
            # just a title
            html.H3('Processing controls'),

            # dropdown menu for processor
            html.Span(className='class__abcd_controls',
                      children=[dcc.Dropdown(id='dropdown-processor',
                                             options=[dict(label='None', value='none'),
                                                      dict(label='ASAP', value='ASAP')], value='ASAP')]),

            # input for asap descriptor string
            html.Br(),
            html.Span(className='class__abcd_controls',
                      children=["Descriptor arguments - SOAP", html.Br(),
                                dcc.Input(className="class__abcd_input_filed",
                                          id='asap_desc_input',
                                          type='text',
                                          placeholder='--l 8 --n 6 --g 0.5 --periodic True --rcut 4.5 --peratom True', )]),

            # input for asap pca string
            html.Br(),
            html.Span(className='class__abcd_controls',
                      children=["PCA arguments", html.Br(),
                                dcc.Input(className="class__abcd_input_filed",
                                          id='asap_pca_input',
                                          type='text',
                                          placeholder='-d 4 --scale True --peratom True --desc-key SOAP-n6-l8-c4.5-g0.5 --fxyz ASAP-n6-l8-c4.5-g0.5.xyz', )]),
        ]),

    ])
    return layout
