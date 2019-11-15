import os, json, shutil, configparser

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import itertools as ito
import numpy as np
import pandas as pd

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
##property_visualize = config['Basic']['property_visualize']
##dimensions = config['Basic']['dimensions']
title = config['Basic']['title']
soap_cutoff_radius = config['Basic']['soap_cutoff_radius']


# read atoms
atoms = ase.io.read(extended_xyz_file,':')
[atoms[i].set_pbc(False) for i in range(len(atoms))]



def build_dataframe_features_molecular_mode(atoms):
    keys = atoms[0].info.keys()
    keys_expanded={}
    for k in keys:
        if isinstance(atoms[0].info[k], np.ndarray):
            print(atoms[0].info[k])
            for i in range(len(atoms[0].info[k])):
                print(k+'_'+str(i))
                keys_expanded[k+'_'+str(i)]=[x.info[k][i] for x in atoms]
        else:
            keys_expanded[k]=[x.info[k] for x in atoms]

    dataframe=pd.DataFrame(data=keys_expanded) 
    return dataframe



if mode =='atomic':
    
#    feature = helpers.get_features_atomic(property_visualize, atoms)
#    p_xyzs = list(ito.chain(*[['mol_{}.xyz'.format(idx)]*len(mol) for idx, mol in enumerate(atoms)]))
#    mols = list(ito.chain(*[[mol]*len(mol) for idx, mol in enumerate(atoms)]))
    # p_xyzs = [item for sublist in p_xzys for item in sublist]
    atomic_numbers = [[i for i,y in enumerate(list(mol.get_chemical_symbols()))] for mol in atoms]
    atomic_numbers = list(np.array(atomic_numbers).flatten())
    # atomic_numbers = helpers.get_features_atomic('numbers', atoms, consider_species)
    system_ids =[]
    for i,mol in enumerate(atoms):
        system_ids+=[i]*len(mol)
    embedding_coordinates = np.asarray(helpers.get_features_atomic(coord_key, atoms))
    c_first_marker = atoms[0].get_positions()[0]
    shapes = [{'type': 'Sphere', "color": "green", 
              "center":{'x': c_first_marker[0],'y': c_first_marker[1],'z': c_first_marker[2]}, 
              "radius":soap_cutoff_radius}]

elif mode in ['compound', 'generic']:
    dataframe=build_dataframe_features_molecular_mode(atoms)
#    feature = helpers.get_features_molecular(property_visualize, atoms)
#    print(feature)
#    p_xyzs = ['mol_{}.xyz'.format(idx) for idx in range(len(atoms))]
#    mols = [mol for mol in atoms]
#    atomic_numbers = [-1]*len(feature)
#    embedding_coordinates = np.asarray(helpers.get_features_molecular(coord_key, atoms))
#    print(embedding_coordinates)
    shapes=[]

# get a periodic box if needed
shapes+=helpers.get_periodic_box_shape_dict(atoms[0])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

default_style = helpers.return_style(atoms[0], default=0)

x_default=dataframe.loc[:, dataframe.columns.tolist()[0]].tolist()
y_default=dataframe.loc[:, dataframe.columns.tolist()[1]].tolist()
size_default=dataframe.loc[:, dataframe.columns.tolist()[2]].tolist()
size_default=np.array(size_default)
size_default=list(size_default-min(size_default)) # cant be smaller than 0

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children=title),

    html.Div([
        html.Span(["x-axis",
            dcc.Dropdown(
                id='x-axis',
                options=[{'label': '{}'.format(i), 'value': i} for i in dataframe.columns],
                value=0)]),
        html.Span(["y-axis",
            dcc.Dropdown(
                id='y-axis',
                options=[{'label': '{}'.format(i), 'value': i} for i in dataframe.columns],
                value=1)]),
        html.Label(["marker_size",
            dcc.Dropdown(
                id='marker_size',
                options=[{'label': '{}'.format(i), 'value': i} for i in dataframe.columns],
                value=2)]),
        html.Label(["marker-color",
            dcc.Dropdown(
                id='marker-color',
                options=[{'label': '{}'.format(i), 'value': i} for i in dataframe.columns],
                value=3)]),
        html.Label(["border-color",
            dcc.Dropdown(
                id='border-color',
                options=[{'label': '{}'.format(i), 'value': i} for i in dataframe.columns],
                value=4)]),
    ], className="two-thirds column"),


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
                        'color': 'rgba(0, 116, 217, 0.7)',
                        'size': size_default,
                        'line': {
                            'color': 'rgb(0, 116, 217)',
                            'width': 0.5
                        },},

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
     dash.dependencies.Input('y-axis', 'value'),
     dash.dependencies.Input('marker_size', 'value')])
def update_graph(x_axis, y_axis, marker_size):

    size_new=dataframe.loc[:, marker_size].tolist()
    size_new=np.array(size_new)
    size_new=list(size_new-min(size_new)) # cant be smaller than 0

    return {'data': [go.Scatter(
                  x = dataframe.loc[:, dataframe.columns.tolist()[x_axis]].tolist(),
                  y = dataframe.loc[:, dataframe.columns.tolist()[y_axis]].tolist(),
                  mode = 'markers',
                  marker= {
                        'color': 'rgba(0, 116, 217, 0.7)',
                        'size': size_new,
                        'line': {
                            'color': 'rgb(0, 116, 217)',
                            'width': 0.5
                        }},

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
    atoms_id = callback_hoverdict["points"][0]["pointNumber"]
    if mode=="atomic": atoms_id = system_ids[atoms_id]
    return json.loads(helpers.ase2json(atoms[atoms_id]))
#    return xyz_reader.read_xyz(ase2xyz(atoms[atom_id]),is_datafile=False)


# Hover over plot -> callback to update style (visualization) of atoms in structure
@app.callback(
    dash.dependencies.Output('3d-viewer', 'styles'),
    [dash.dependencies.Input('graph', 'hoverData')]
    )
def return_style_callback(callback_hoverdict, default=-1):
  
    atoms_id = callback_hoverdict["points"][0]["pointNumber"]
    if mode=="atomic": atoms_id = system_ids[atoms_id]
    if default==-1: atoms_id = atoms[atoms_id]
    else: atoms_id = atoms[default]

    return helpers.return_style(atoms_id, default=-1)


# Hover over plot -> callback to update shapes (box, marker) of atomic env in structure
@app.callback(
    dash.dependencies.Output('3d-viewer', 'shapes'),
    [dash.dependencies.Input('graph', 'hoverData')]
    )
def return_shape_callback(callback_hoverdict, default=-1):
    print(callback_hoverdict)
    atoms_id = callback_hoverdict["points"][0]["pointNumber"]
    callback_id = callback_hoverdict["points"][0]["pointNumber"]
    if mode=="atomic": atoms_id = system_ids[atoms_id]
    if default==-1: atoms_id = atoms[atoms_id]
    else: atoms_id = atoms[default]

    shapes=[]
    if mode=='atomic': 
        pos = atoms_id.get_positions()[atomic_numbers[callback_id]]
        shapes = [{'type': 'Sphere', "color": "green", 
                                  "center":{'x': pos[0],'y': pos[1],'z': pos[2]}, 
                                  "radius":soap_cutoff_radius}]
    shapes+=helpers.get_periodic_box_shape_dict(atoms_id)
    return shapes



app.run_server(debug=False, port=9999)

