import os, json, shutil, configparser

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import itertools as ito
import numpy as np

import ase.io

import helpers

import dash_bio as dashbio

import dash_bio_utils.xyz_reader as xyz_reader

from rtools.helpers.converters import ase2xyz

# read config
config = configparser.ConfigParser()
config.read('config.txt')
extended_xyz_file =   config['Basic']['extended_xyz_file']
mode = config['Basic']['mode']
coord_key = config['Basic']['coord_key']
property_visualize = config['Basic']['property_visualize']
dimensions = config['Basic']['dimensions']
title = config['Basic']['title']
soap_cutoff_radius = config['Basic']['soap_cutoff_radius']


# read atoms
atoms = ase.io.read(extended_xyz_file,':')
[atoms[i].set_pbc(False) for i in range(len(atoms))]

print(atoms[0].info)

# collect data
#consider_species = config['Basic']['consider_species']
#if '[' in consider_species:
#    consider_species = list(consider_species)
#elif consider_species == 'all':
#    consider_species = list(set(ito.chain(*[atoms_i.get_chemical_symbols() for atoms_i in atoms])))
#else:
#    consider_species = str(consider_species)



if mode =='atomic':
    feature = helpers.get_features_atomic(property_visualize, atoms)
    p_xyzs = list(ito.chain(*[['mol_{}.xyz'.format(idx)]*len(mol) for idx, mol in enumerate(atoms)]))
    mols = list(ito.chain(*[[mol]*len(mol) for idx, mol in enumerate(atoms)]))
    # p_xyzs = [item for sublist in p_xzys for item in sublist]
    atomic_numbers = [range(len(mol)) for mol in atoms]
    atomic_numbers = list(np.array(atomic_numbers).flatten())
    # atomic_numbers = helpers.get_features_atomic('numbers', atoms, consider_species)
    embedding_coordinates = np.asarray(helpers.get_features_atomic(coord_key, atoms, consider_species))
    c_first_marker = atoms[0][0].positions
    print(c_first_marker)
    shapes = [{'type': 'Sphere', "color": "green", 
              "center":{'x': c_first_marker[0],'y': c_first_marker[1],'z': c_first_marker[2]}, 
              "radius":soap_cutoff_radius}]

elif mode in ['compound', 'generic']:
    feature = helpers.get_features_molecular(property_visualize, atoms)
#    print(feature)
    p_xyzs = ['mol_{}.xyz'.format(idx) for idx in range(len(atoms))]
    mols = [mol for mol in atoms]
    atomic_numbers = [-1]*len(feature)
    embedding_coordinates = np.asarray(helpers.get_features_molecular(coord_key, atoms))
#    print(embedding_coordinates)
    shapes=[]

shapes+=helpers.get_periodic_box_shape_dict(atoms[0])



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

default_style = helpers.return_style(atoms[0], default=0)

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children=title),

    html.Div([
        html.Span(["x-axis",
            dcc.Dropdown(
                id='x-axis',
                options=[{'label': 'Dimension {}'.format(i), 'value': i} for i in range(embedding_coordinates.shape[1])],
                value=0)]),
        html.Span(["y-axis",
            dcc.Dropdown(
                id='y-axis',
                options=[{'label': 'Dimension {}'.format(i), 'value': i} for i in range(embedding_coordinates.shape[1])],
                value=1)]),
        html.Label(["marker-size",
            dcc.Dropdown(
                id='marker-size',
                options=[{'label': 'Dimension {}'.format(i), 'value': i} for i in range(embedding_coordinates.shape[1])],
                value=1)]),
        html.Label(["marker-color",
            dcc.Dropdown(
                id='marker-color',
                options=[{'label': 'Dimension {}'.format(i), 'value': i} for i in range(embedding_coordinates.shape[1])],
                value=1)]),
    ], className="two-thirds column"),


    html.Div([
        dcc.Graph(
            id='graph',
            hoverData={},
            figure={
                'data': [
                    {'x': embedding_coordinates[:, 0].tolist(),
                     'y': embedding_coordinates[:, 1].tolist(),
                     'mode': 'markers',
                     'name': 'TODO'},
                ],
                'layout': {
                    'title': 'Data Visualization',
                     'height': 600,
                }
            }
        )
        ], style={'width': '75%'}),

     
     html.Div([
        dashbio.Molecule3dViewer(
        id='3d-viewer',
        styles = default_style, 
        shapes = shapes,
        modelData = json.loads(helpers.ase2json(atoms[0]))),
        "Compound-view",
        html.Hr(),
        html.Div(id='molecule3d-output')
        ])

])



@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('x-axis', 'value'),
     dash.dependencies.Input('y-axis', 'value')])
def update_graph(x_axis, y_axis):

    return {'data': [go.Scatter(
                  x = embedding_coordinates[:, x_axis].tolist(),
                  y = embedding_coordinates[:, y_axis].tolist(),
                  mode = 'markers',
                  name = 'TODO',
                    )],
            'layout': go.Layout(
                 title = 'Data Visualization'
                 )
            }

# Hover over plot -> callback to update structure
@app.callback(
    dash.dependencies.Output('3d-viewer', 'modelData'),
    [dash.dependencies.Input('graph', 'hoverData')]
    )
def show_atoms(callback_hoverdict):
    print(callback_hoverdict)
    atom_id = callback_hoverdict["points"][0]["pointNumber"]
    return json.loads(helpers.ase2json(atoms[atom_id]))
#    return xyz_reader.read_xyz(ase2xyz(atoms[atom_id]),is_datafile=False)


# Hover over plot -> callback to update style (visualization) of atoms in structure
@app.callback(
    dash.dependencies.Output('3d-viewer', 'styles'),
    [dash.dependencies.Input('graph', 'hoverData')]
    )
def return_style_callback(callback_hoverdict, default=-1):

    if default==-1: atoms_id = atoms[callback_hoverdict["points"][0]["pointNumber"]]
    else: atoms_id = atoms[default]

    return helpers.return_style(atoms_id, default=-1)


# Hover over plot -> callback to update shapes (box, marker) of atomic env in structure
@app.callback(
    dash.dependencies.Output('3d-viewer', 'shapes'),
    [dash.dependencies.Input('graph', 'hoverData')]
    )
def return_shape_callback(callback_hoverdict, default=-1):

    if default==-1: atoms_id = atoms[callback_hoverdict["points"][0]["pointNumber"]]
    else: atoms_id = atoms[default]

    shapes=[]
    if mode=="atomic": shapes = [{'type': 'Sphere', "color": "green", 
                                  "center":{'x': 0,'y': 0,'z': -2.5}, 
                                  "radius":soap_cutoff_radius}]
    shapes=helpers.get_periodic_box_shape_dict(atoms_id)
    return shapes



app.run_server(debug=False, port=9999)

