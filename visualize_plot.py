#!python3

import argparse
import configparser
import json
import sys
import copy
from copy import deepcopy

import ase.io
import dash
import dash_bio
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go

import helpers

callback_hoverdict_global = [] # necessary global variable
list_hovertexts=[]

def main(config_filename, extended_xyz_file, mode, title, soap_cutoff_radius, marker_radius, height_graph, width_graph):
    global callback_hoverdict_global, list_hovertexts

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
        width_graph = int(config['Basic']['height_graph'])

    # read atoms
    atoms = ase.io.read(extended_xyz_file, ':')
    #[atoms[i].set_pbc(False) for i in range(len(atoms))]

    # Setup of the dataframes and atom/molecular infos for the 3D-Viewer
    shapes = []
    dataframe = helpers.build_dataframe_features(atoms, mode=mode)
    if mode == 'atomic':
        c_first_marker = atoms[0].get_positions()[0]
        system_ids = dataframe['system_ids']
        atomic_numbers = dataframe['atomic_numbers']
        dataframe.drop(['atomic_numbers', 'system_ids'], axis=1, inplace=True)


    # add a periodic box if needed
    shapes += helpers.get_periodic_box_shape_dict(atoms[0])

    # Initial data for the graph and 3D viewer
    default_style = helpers.return_style(atoms[0], default=0)
    x_default = dataframe[dataframe.columns.tolist()[0]].tolist()
    y_default = dataframe[dataframe.columns.tolist()[1]].tolist()
    size_default = dataframe[dataframe.columns.tolist()[2]].tolist()
    size_default = np.array(size_default)
    size_default = list(size_default - min(size_default))  # cant be smaller than 0
    color_default = dataframe[dataframe.columns.tolist()[3]].tolist()
    colorbar_title = dataframe.columns.tolist()[3]
    style_dropdown = {'height': '35px', 'width': '100%', 'display': 'inline-block'}
    

    list_hovertexts=helpers.get_hoverinfo_texts(dataframe)
 
    # Setup of app
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.H3(children=title),

        html.Div([
            html.Span(["x-axis", html.Br(),
                       dcc.Dropdown(
                           id='x-axis',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=0, style=style_dropdown)], className='app__dropdown'),
            html.Span(['y-axis',
                       dcc.Dropdown(
                           id='y-axis',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=1, style=style_dropdown)], className='app__dropdown'),
            html.Span(["marker-size",
                       dcc.Dropdown(
                           id='marker_size',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=2, style=style_dropdown)], className='app__dropdown'),
            html.Span(["marker-color",
                       dcc.Dropdown(
                           id='marker_color',
                           options=[{'label': '{}'.format(l), 'value': i} for i, l in enumerate(dataframe.columns)],
                           value=3, style=style_dropdown)], className='app__dropdown'),
            html.Span(['marker-opacity', html.Br(),
                       dcc.Input(
                           id='marker_opacity',
                           type='text',
                           placeholder='marker opacity (0 to 1)')], className='app__dropdown'),
            html.Span(['colorscale', html.Br(),
                       dcc.Input(
                           id='colorscale',
                           type='text',
                           placeholder='colormap name')], className='app__dropdown'),
       ], className="app__controls"),


        html.Div([
            html.Span(["marker-size-range",
                       dcc.RangeSlider(
                           id='marker_size_range',
                           min=1, max=100, step=0.1, value=[5, 50],
                           marks={s: s for s in range(0, 101, 10)},
                           allowCross=False,
                       )], className='app__slider'),
            html.Span(["marker-size-limits",
                       dcc.RangeSlider(
                           id='marker_size_limits',
                           min=0, max=100, step=0.1, value=[0, 100],
                           marks={p: '{}%'.format(p) for p in range(0, 101, 10)},
                           allowCross=False,
                       )], className='app__slider'),
            html.Span(["marker-color-limits",
                       dcc.RangeSlider(
                           id='marker_color_limits',
                           min=0, max=100, step=0.1, value=[0, 100],
                           marks={p: '{}%'.format(p) for p in range(0, 101, 10)},
                           allowCross=False,
                       )], className='app__slider'),
            html.Br(),
            html.Br(),
        ], className='app__controls'),
       
 

        # placeholder by graph, now filled in by callback on startup
        html.Div([
            dcc.Graph(
                id='graph',
                figure={
                    'data': [], 'layout': {}
                }
            )
        ], className='app__container_scatter'),


        html.Div([
                html.Span(['Periodic repetition of structure: ', dcc.Input(id='periodic_repetition_structure', type='text', placeholder='(0,1) (0,1) (0,1)')], className='app__remarks_viewer'),
                dcc.Markdown('''
                            **Axis:**  &nbsp;&nbsp; x : red  &nbsp;&nbsp; y : green &nbsp;&nbsp; z : blue   
                            **Green sphere:** Selected atom marker.  &nbsp;&nbsp;**Gray wireframe:** SOAP cutoff.  
                            **Mouse-Navigation:**  &nbsp;&nbsp;*Mouse:* Rotate,  &nbsp;&nbsp;*Ctrl+Mouse:* Translate,  &nbsp;&nbsp;*Shift+Mouse:* Zoom''', className='app__remarks_viewer'),
                dcc.Loading(html.Div([
                dash_bio.Molecule3dViewer(
                    id='3d-viewer',
                    styles=default_style,
                    shapes=shapes,
                    modelData=json.loads(helpers.ase2json(atoms[0])))], id='div-3dviewer')),
                   ], className='app__container_3dmolviewer', style={'height': height_graph, 'width_graph': width_graph}),


        ],
        className='app-body')



    # Callbacks that update the viewer

    @app.callback(
        dash.dependencies.Output('graph', 'figure'),
        [dash.dependencies.Input('x-axis', 'value'),
         dash.dependencies.Input('y-axis', 'value'),
         dash.dependencies.Input('marker_size', 'value'),
         dash.dependencies.Input('marker_size_range', 'value'),
         dash.dependencies.Input('marker_size_limits', 'value'),
         dash.dependencies.Input('marker_color', 'value'),
         dash.dependencies.Input('marker_color_limits', 'value'),
         dash.dependencies.Input('colorscale', 'value'),
         dash.dependencies.Input('marker_opacity','value'),])
    def update_graph(x_axis, y_axis, marker_size, marker_size_range, marker_size_limits, marker_color, marker_color_limits, colorscale, marker_opacity):

        global list_hovertexts        

        color_new = dataframe[dataframe.columns.tolist()[marker_color]]
        # color limits
        color_new = copy.copy(dataframe[dataframe.columns.tolist()[marker_color]])
        color_span = np.abs(np.max(color_new) - np.min(color_new))
        color_new_lower = np.min(color_new) + color_span / 100. * marker_color_limits[0]
        color_new_upper = np.min(color_new) + color_span / 100. * marker_color_limits[1]
        indices_in_limits = np.asarray(
            [idx for idx, val in enumerate(color_new) if color_new_lower <= val <= color_new_upper])
        
        color_new_min = np.min(color_new)
        color_new_max = np.max(color_new)
        color_new_lower = color_new_min + color_span / 100. * marker_color_limits[0]
        color_new_upper = color_new_min + color_span / 100. * marker_color_limits[1]

        size_new = dataframe[dataframe.columns.tolist()[marker_size]].tolist()
        size_new = np.array(size_new)
        size_new = size_new - min(size_new)  # cant be smaller than 0
        
        #opacity
        if marker_opacity==None: 
            marker_opacity=1.0
        else:
            try:
                # convert to float here and check if value was valid
                marker_opacity = float(marker_opacity)
                if marker_opacity < 0. or marker_opacity > 1.:
                    raise ValueError
            except ValueError:
                print('Marker opacity set: {} ; Invalid, set to 1.0 be default.'.format(marker_opacity))
                marker_opacity = 1.0
        size_new = copy.copy(dataframe[dataframe.columns.tolist()[marker_size]].tolist())
        size_new = np.array(size_new)
        size_new = size_new - np.min(size_new)  # cant be smaller than 0
        size_new_range = np.max(size_new)
        size_new_lower = size_new_range/100.*marker_size_limits[0]
        size_new_upper = size_new_range/100.*marker_size_limits[1]

        try:
            for idx, size_new_i in enumerate(size_new):
                if size_new_i < size_new_lower:
                    size_new[idx] = marker_size_range[0]
                elif size_new_i > size_new_upper:
                    size_new[idx] = marker_size_range[1]
                else:
                    size_new[idx] = _get_new_sizes(size_new_i, [size_new_lower, size_new_upper], marker_size_range)
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

        return {'data': [go.Scattergl(
            x=dataframe[dataframe.columns.tolist()[x_axis]].tolist(),
            y=dataframe[dataframe.columns.tolist()[y_axis]].tolist(),
            mode='markers',
            hovertext=list_hovertexts,
            marker={
                'color': color_new,
                'colorscale': 'Viridis' if colorscale is None or colorscale == '' else colorscale,
                'size': size_new,
                'colorbar': {'title': dataframe.columns.tolist()[marker_color]},
                'opacity': float(marker_opacity),
                'cmin' : color_new_lower,
                'cmax' : color_new_upper,
                'line': {
                    'color': 'rgb(0, 116, 217)',
                    'width': 0.5
                }},

            name='TODO',
        )],
            'layout': go.Layout(height=height_graph,
            
                                hovermode='closest',
                                #         title = 'Data Visualization'
                                xaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside', 'automargin': True,
                                       'showline': True, 'mirror': True, 'title': dataframe.columns.tolist()[x_axis]},
                                yaxis={'zeroline': False, 'showgrid': False, 'ticks': 'outside', 'automargin': True,
                                       'showline': True, 'mirror': True, 'title': dataframe.columns.tolist()[y_axis]}
                                )
        }

       

    def _get_new_sizes(value, value_range, size_range):
        """Map ``value`` to a range within ``size_range`` in a linear fashion."""
        slope = (size_range[1] - size_range[0]) / float(value_range[1]- value_range[0])
        return size_range[0] + slope * (value - value_range[0])

    def return_shape_callback(atoms_current, pos_marker=None, default=-1, shift_cell=np.array([0.,0.,0.])):
        
        shapes=[]

        if isinstance(pos_marker, np.ndarray) or isinstance(pos_marker, list):
            shapes = [{'type': 'Sphere', "color": "gray",
                       "center": {'x': pos_marker[0], 'y': pos_marker[1], 'z': pos_marker[2]},
                       "radius": soap_cutoff_radius, 'wireframe': True},
                      {'type': 'Sphere', "color": "green",
                       "center": {'x': pos_marker[0], 'y': pos_marker[1], 'z': pos_marker[2]},
                       "radius": marker_radius}
                      ]
        
        shape_box = helpers.get_periodic_box_shape_dict(atoms_current, shift_cell)
        shapes += shape_box
        return shapes



    def return_modelData_atoms(atoms_id, periodic_repetition_str='(0,1) (0,1) (0,1)'):

        if mode == "atomic":
            atoms_current = atoms[system_ids[atoms_id]]
            pos_marker = atoms_current.get_positions()[atomic_numbers[atoms_id]]
        else:
            print(atoms_id)
            atoms_current = atoms[atoms_id]
            pos_marker=None

        shift_cell=np.array([0.,0.,0.])
        cell = atoms_current.get_cell() 

        if periodic_repetition_str!='(0,1) (0,1) (0,1)' and np.sum(atoms_current.get_pbc())>0:
           
            x_rep, y_rep, z_rep = periodic_repetition_str.split(' ')
            x_rep = [int(x) for x in x_rep[1:-1].split(',')]
            x_multi = x_rep[1]-x_rep[0]
            y_rep = [int(y) for y in y_rep[1:-1].split(',')]
            y_multi = y_rep[1]-y_rep[0]
            z_rep = [int(z) for z in z_rep[1:-1].split(',')]
            z_multi = z_rep[1]-z_rep[0]
         
            #shift_cell = atoms_current.get_center_of_mass()
            atoms_current = deepcopy(atoms_current)*np.array([x_multi, y_multi, z_multi])

            # shift correctly, we need to correct for the viewers automatic com centering
            new_positions = np.array([ x+(cell[0]*x_rep[0]+cell[1]*y_rep[0]+cell[2]*z_rep[0]) for x in atoms_current.get_positions()])
            atoms_current.set_positions(new_positions)
            atoms_current.set_cell(cell)

        shapes = return_shape_callback(atoms_current, pos_marker, shift_cell=shift_cell)

        return json.loads( helpers.ase2json( atoms_current ) ), shapes, atoms_current


    @app.callback(
        dash.dependencies.Output('div-3dviewer', 'children'),
        [dash.dependencies.Input('graph', 'clickData'), 
         dash.dependencies.Input('periodic_repetition_structure','value')])
    def update_3dviewer(callback_hoverdict, periodic_repetition_structure, default=-1):
        
        global callback_hoverdict_global

        run_update=True

        if periodic_repetition_structure == None:
            periodic_repetition_structure='(0,1) (0,1) (0,1)' 
        elif not periodic_repetition_structure.count('(')==3 or not periodic_repetition_structure.count(')')==3:
            run_update=False
              
        if not run_update: raise Exception('no update required')
        
        if not callback_hoverdict==None: 
            callback_hoverdict_global = callback_hoverdict
        
        if callback_hoverdict_global==[]: atoms_id = 0
        else:
            atoms_id = callback_hoverdict_global["points"][0]["pointNumber"] 
        
        modelData, shapes, atoms_current = return_modelData_atoms(atoms_id, periodic_repetition_str=periodic_repetition_structure)
        styles = helpers.return_style(atoms_current)
         
        view = dash_bio.Molecule3dViewer(
                    id='3d-viewer',
                    styles=styles,
                    shapes=shapes,
                    modelData= modelData)#modelData) #])),

        return view

    app.run_server(debug=False, port=9999)


if __name__ == "__main__":
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

    sys.exit(main(extended_xyz_file=args.fxyz,
                  height_graph=args.height,
                  width_graph=args.width,
                  mode=args.mode,
                  title=args.title,
                  config_filename=args.config_file,
                  marker_radius=args.marker_radius,
                  soap_cutoff_radius=args.soap_cutoff))
