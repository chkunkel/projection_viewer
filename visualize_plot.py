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

import dash_bio
from importlib import reload

import dash_bio_utils.xyz_reader as xyz_reader

from rtools.helpers.converters import ase2xyz

# read config
config = configparser.ConfigParser()
config.read('config.txt')
extended_xyz_file =   config['Basic']['extended_xyz_file']
mode = config['Basic']['mode']
coord_key = config['Basic']['coord_key']
title = config['Basic']['title']
soap_cutoff_radius = config['Basic']['soap_cutoff_radius']
height_graph=530

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


# Setup of the dataframes and atom/molecular infos for the 3D-Viewer
if mode =='atomic':
    atomic_numbers = [[i for i,y in enumerate(list(mol.get_chemical_symbols()))] for mol in atoms]
    atomic_numbers = list(np.array(atomic_numbers).flatten())
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
    shapes=[]

# get a periodic box if needed
shapes+=helpers.get_periodic_box_shape_dict(atoms[0])

# Initial data for the graph and 3D viewer
default_style = helpers.return_style(atoms[0], default=0)
x_default=dataframe.loc[:, dataframe.columns.tolist()[0]].tolist()
y_default=dataframe.loc[:, dataframe.columns.tolist()[1]].tolist()
size_default=dataframe.loc[:, dataframe.columns.tolist()[2]].tolist()
size_default=np.array(size_default)
size_default=list(size_default-min(size_default)) # cant be smaller than 0
color_default=dataframe.loc[:, dataframe.columns.tolist()[3]].tolist()
colorbar_title=dataframe.columns.tolist()[3]
style_dropdown={'height': '35px', 'width': '100%', 'display':'inline-block'}

# Setup of app
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.Div(children=title, className='what-is'),

    html.Div([
        html.Span(["x-axis", html.Br(),
            dcc.Dropdown(
                id='x-axis',
                options=[{'label': '{}'.format(l), 'value': i} for i,l in enumerate(dataframe.columns)],
                value=0, style=style_dropdown)], className='app__dropdown', style={'width': '25%', 'display':'inline-block'}), 
        html.Span(['y-axis',
            dcc.Dropdown(
                id='y-axis',
                options=[{'label': '{}'.format(l), 'value': i} for i,l in enumerate(dataframe.columns)],
                value=1, style=style_dropdown)], className='app__dropdown', style={'width': '25%', 'display':'inline-block'}),
        html.Span(["marker-size",
            dcc.Dropdown(
                id='marker_size',
                options=[{'label': '{}'.format(l), 'value': i} for i,l in enumerate(dataframe.columns)],
                value=2, style=style_dropdown)],  className='app__dropdown', style={'width': '25%', 'display':'inline-block'}),
        html.Span(["marker-color",
            dcc.Dropdown(
                id='marker_color',
                options=[{'label': '{}'.format(l), 'value': i} for i,l in enumerate(dataframe.columns)],
                value=3, style=style_dropdown)], className='app__dropdown', style={'width': '25%', 'display':'inline-block'}),
    ], className="app__dropdown"),


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
                        'color': color_default,
                        'colorscale':"Viridis",
                        'colorbar':{'title' : colorbar_title},
                        'size': size_default,
                        'line': {
                            'color': 'rgb(0, 116, 217)', #todo: implement border color option
                            'width': 0.5
                        },},

                     'name': 'TODO'},
                ],
                'layout': {
                     'xaxis': { 'zeroline': False },
                     'yaxis': { 'zeroline': False },
                    #'title': 'Data Visualization',
                     'height': height_graph,
                }
            }
        )
        ], style={'width': '63%', 'display': 'inline-block'}),

     
     html.Div([dcc.Loading(html.Div([
        dash_bio.Molecule3dViewer(
            id='3d-viewer',
            styles = default_style, 
            shapes = shapes,
            modelData = json.loads(helpers.ase2json(atoms[0]))),
            html.Div(id='molecule3d-output')
            ], 
         id='div-3dviewer'))], className='container bg-white p-0' ,style={'vertical-align':'center', 'width': '35.5%', 'display': 
                                                                          'inline-block', 'border-style':'solid', 'height':height_graph})], 
       className='app-body')



@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('x-axis', 'value'),
     dash.dependencies.Input('y-axis', 'value'),
     dash.dependencies.Input('marker_size', 'value'),
     dash.dependencies.Input('marker_color', 'value')])
def update_graph(x_axis, y_axis, marker_size, marker_color):

    size_new=dataframe.loc[:, dataframe.columns.tolist()[marker_size]].tolist()
    size_new=np.array(size_new)
    size_new=list(size_new-min(size_new)) # cant be smaller than 0
    color_new = dataframe.loc[:, dataframe.columns.tolist()[marker_color]].tolist()

    return {'data': [go.Scatter(
                  x = dataframe.loc[:, dataframe.columns.tolist()[x_axis]].tolist(),
                  y = dataframe.loc[:, dataframe.columns.tolist()[y_axis]].tolist(),
                  mode = 'markers',
                  marker= {
                        'color': color_new,
                        'colorscale':'Viridis',
                        'size': size_new,
                        'colorbar':{'title' : dataframe.columns.tolist()[marker_color]},
                        'line': {
                            'color': 'rgb(0, 116, 217)',
                            'width': 0.5
                        }},

                  name = 'TODO',
                    )],
            'layout': go.Layout( height=height_graph,
           #         title = 'Data Visualization'
                     xaxis = { 'zeroline': False , 'showgrid': False, 'ticks':'outside',
                               'showline': True, 'mirror':True, 'title':dataframe.columns.tolist()[x_axis] },
                     yaxis = { 'zeroline': False , 'showgrid': False, 'ticks':'outside', 
                               'showline': True, 'mirror':True,'title':dataframe.columns.tolist()[y_axis] }
                 )
            }

# Hover over plot -> callback to update structure
#@app.callback(
#    dash.dependencies.Output('3d-viewer', 'modelData'),
#    [dash.dependencies.Input('graph', 'hoverData')]
#    )
def show_atoms(callback_hoverdict):
    print(callback_hoverdict)
    atoms_id = callback_hoverdict["points"][0]["pointNumber"]
    if mode=="atomic": atoms_id = system_ids[atoms_id]
    return json.loads(helpers.ase2json(atoms[atoms_id]))


# Hover over plot -> callback to update style (visualization) of atoms in structure
#@app.callback(
#    dash.dependencies.Output('3d-viewer', 'styles'),
#    [dash.dependencies.Input('graph', 'hoverData')]
#    )
def return_style_callback(callback_hoverdict, default=-1):
  
    atoms_id = callback_hoverdict["points"][0]["pointNumber"]
    if mode=="atomic": atoms_id = system_ids[atoms_id]
    if default==-1: atoms_id = atoms[atoms_id]
    else: atoms_id = atoms[default]

    return helpers.return_style(atoms_id, default=-1)


# Hover over plot -> callback to update shapes (box, marker) of atomic env in structure
#@app.callback(
#    dash.dependencies.Output('3d-viewer', 'shapes'),
#    [dash.dependencies.Input('graph', 'hoverData')]
#    )
def return_shape_callback(callback_hoverdict, default=-1):
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


@app.callback(
    dash.dependencies.Output('div-3dviewer', 'children'),
    [dash.dependencies.Input('graph', 'hoverData')])
def update_3dviewer(callback_hoverdict, default=-1):

    shapes = return_shape_callback(callback_hoverdict, default=-1)
    styles = return_style_callback(callback_hoverdict, default=-1)
    modelData = show_atoms(callback_hoverdict)
    

    view = dash_bio.Molecule3dViewer(
        styles = styles,
        shapes = shapes,
        modelData = modelData)
    return view

app.run_server(debug=False, port=9999)

