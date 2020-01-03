import json
from copy import deepcopy

import ase
import ase.io
import dash_bio
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from dash import Dash


def get_features_molecular(feature, atoms):
    """Returns a list with the molecular feature for all geometries in `atoms`"""
    return [atoms_i.info[feature] for atoms_i in atoms]


def get_features_atomic(feature, atoms):
    """Returns a list with the atomic features for all geometries in `atoms`"""
    features = []
    for atoms_i in atoms:
        features.extend(
            [feature_i for feature_i, symbol_i in zip(atoms_i.arrays[feature], atoms_i.get_chemical_symbols())])
    return features


def get_atomic_numbers(atoms):
    """Returns a list with the atomic numbers for all geometries in `atoms`"""
    atomic_numbers = []
    for atoms_i in atoms:
        atomic_numbers.extend(
            [number for number, symbol in zip(atoms_i.get_atomic_numbers(), atoms_i.get_chemical_symbols())])
    return atomic_numbers


def ase2json(atoms_ase):
    """
    Converts ase.Atoms to JSON for Molecule3dViewer

    Note: translates molecule by CoM, so everything else needs to be translated in the viewer as well!
    """
    atoms_ase.translate(atoms_ase.get_center_of_mass() * -1)
    json_str = '{"atoms": ['
    for i, pos in enumerate(atoms_ase.get_positions()):
        elem = str(atoms_ase.get_chemical_symbols()[i])
        json_str += '{"name":"' + elem + '","chain":"A","residue_index":0,"residue_name":"A", "serial": "' + str(
            i) + '","element":"' + elem + '", "positions":' + str(list(pos)) + '}'
        if not i == len(atoms_ase) - 1:
            json_str += ","
    json_str += '], "bonds": [], "pbc": {}, "cell": {}}}'.format(str(atoms_ase.get_pbc().tolist()).lower(),
                                                                 atoms_ase.get_cell().tolist())

    return json_str


def json2atoms(at_json):
    try:
        at_decoded = json.loads(at_json)
    except TypeError:
        # of dict is given
        at_decoded = at_json

    symbols = []
    pos_list = []

    for item in at_decoded['atoms']:
        symbols.append(item['name'])
        pos_list.append(item['positions'])

    ase_at = ase.Atoms(symbols=symbols, positions=pos_list, cell=at_decoded['cell'], pbc=at_decoded['pbc'])

    return ase_at


def get_hex_color(c_rgb):
    return '#%02x%02x%02x' % (c_rgb[0], c_rgb[1], c_rgb[2])


def return_atom_list_style_for_3d_view(ase_atoms):
    dict_style = {}
    for i, at in enumerate(ase_atoms):
        hex_color = get_hex_color([int(x * 255) for x in jmol_colors[ase_atoms.get_atomic_numbers()[i]]])
        # hex_color = '#%02x%02x%02x' % (c_rgb[0], c_rgb[1], c_rgb[2])
        dict_style[str(i)] = {"color": hex_color, "visualization_type": "sphere",
                              "radius": covalent_radii[ase_atoms.get_atomic_numbers()[i]]}
    return dict_style


# check whether a periodic box is needed to be drawn, and return it as a shape if needed
def get_periodic_box_shape_dict(atoms_ase):
    # so far we only show a box when it is 3d periodic
    if not np.any(atoms_ase.get_cell_lengths_and_angles()[0:3] > 0): return []

    # point0 = np.array([0.0, 0.0, 0.0])
    point0 = -atoms_ase.get_center_of_mass()
    lattice_vectors = atoms_ase.get_cell()
    point1 = list(point0 + lattice_vectors[0])
    point2 = list(point0 + lattice_vectors[1])
    point3 = list(point0 + lattice_vectors[2])
    point4 = list(point2 + lattice_vectors[2])
    point5 = list(point1 + lattice_vectors[1])
    point6 = list(point1 + lattice_vectors[2])
    point7 = list(point4 + lattice_vectors[0])
    point0 = list(point0)

    shapes = []
    shapes.append({"type": "Cylinder", "color": get_hex_color([0, 0, 255]),
                   "start": {"x": point0[0], "y": point0[1], "z": point0[2]},
                   "end": {"x": point1[0], "y": point1[1], "z": point1[2]}})
    shapes.append({"type": "Cylinder", "color": get_hex_color([255, 0, 0]),
                   "start": {"x": point0[0], "y": point0[1], "z": point0[2]},
                   "end": {"x": point2[0], "y": point2[1], "z": point2[2]}})
    shapes.append({"type": "Cylinder", "color": get_hex_color([0, 255, 0]),
                   "start": {"x": point0[0], "y": point0[1], "z": point0[2]},
                   "end": {"x": point3[0], "y": point3[1], "z": point3[2]}})

    black = get_hex_color([255, 255, 255])
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point1[0], "y": point1[1], "z": point1[2]},
                   "end": {"x": point5[0], "y": point5[1], "z": point5[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point1[0], "y": point1[1], "z": point1[2]},
                   "end": {"x": point6[0], "y": point6[1], "z": point6[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point2[0], "y": point2[1], "z": point2[2]},
                   "end": {"x": point4[0], "y": point4[1], "z": point4[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point2[0], "y": point2[1], "z": point2[2]},
                   "end": {"x": point5[0], "y": point5[1], "z": point5[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point3[0], "y": point3[1], "z": point3[2]},
                   "end": {"x": point4[0], "y": point4[1], "z": point4[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point3[0], "y": point3[1], "z": point3[2]},
                   "end": {"x": point6[0], "y": point6[1], "z": point6[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point4[0], "y": point4[1], "z": point4[2]},
                   "end": {"x": point7[0], "y": point7[1], "z": point7[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point5[0], "y": point5[1], "z": point5[2]},
                   "end": {"x": point7[0], "y": point7[1], "z": point7[2]}})
    shapes.append({"type": "Cylinder", "color": black,
                   "start": {"x": point6[0], "y": point6[1], "z": point6[2]},
                   "end": {"x": point7[0], "y": point7[1], "z": point7[2]}})

    return shapes


'''
This is taken from rtools.helpers.converters
Courtesy of Simon Rittmeyer and Christoph Schober
We didn't want to steal it, but wanted to avoid a further dependency
'''

try:
    import StringIO as io
except ImportError:
    import io


def ase2xyz(atoms):
    """
    Prepare a XYZ string from an ASE atoms object.
    """
    # Implementation detail: If PBC should be implemented, the
    # write to xyz needs to be changed to include cell etc.
    if any(atoms.get_pbc()):
        raise RuntimeError("Detected PBCs. Not supported (yet)!")
    num_atoms = len(atoms)
    types = atoms.get_chemical_symbols()
    all_atoms = zip(types, atoms.get_positions())
    a_str = str(num_atoms) + "\n" + "\n"
    for atom in all_atoms:
        a_str += atom[0] + " " + " ".join([str(x) for x in atom[1]]) + "\n"
    return a_str


def build_dataframe_features(atoms, mode='molecular'):
    if mode == 'atomic':
        keys = atoms[0].arrays.keys()
    else:
        keys = atoms[0].info.keys()

    keys_expanded = {}

    if mode == 'atomic':
        at_numbers = [[i for i, y in enumerate(list(mol.get_chemical_symbols()))] for mol in atoms]
        at_numbers = list(np.array(at_numbers).flatten())
        sys_ids = []
        for i, mol in enumerate(atoms):
            sys_ids += [i] * len(mol)
        keys_expanded['system_ids'] = sys_ids
        keys_expanded['atomic_numbers'] = at_numbers

    for k in keys:
        if mode == 'atomic':
            if len(atoms[0].arrays[k].shape) > 1:
                for i in range(atoms[0].arrays[k].shape[1]):
                    print(k, i)
                    keys_expanded[k + '_' + str(i)] = np.array(
                        [[x.arrays[k][j][i] for j in range(len(x))] for x in atoms]).flatten()
                    print(np.array(keys_expanded[k + '_' + str(i)]).shape)
            else:
                keys_expanded[k] = np.array([[x.arrays[k][j] for j in range(len(x))] for x in atoms]).flatten()
                print(k, len(keys_expanded[k]))
                continue

        else:
            if isinstance(atoms[0].info[k], np.ndarray):
                for i in range(len(atoms[0].info[k])):
                    keys_expanded[k + '_' + str(i)] = [x.info[k][i] for x in atoms]
            else:
                keys_expanded[k] = [x.info[k] for x in atoms]

    df = pd.DataFrame(data=keys_expanded)

    return df


def get_new_sizes(value, value_range, size_range):
    """Map ``value`` to a range within ``size_range`` in a linear fashion."""
    slope = (size_range[1] - size_range[0]) / float(value_range[1] - value_range[0])
    return size_range[0] + slope * (value - value_range[0])


def process_marker_opacity_value(marker_opacity_value):
    """
    Process string input of marker_opacity_value

    :param marker_opacity_value: str
    :return:
    """

    if marker_opacity_value == None:
        marker_opacity_value = 1.0
    else:
        try:
            # convert to float here and check if value was valid
            marker_opacity_value = float(marker_opacity_value)
            if marker_opacity_value < 0. or marker_opacity_value > 1.:
                raise ValueError
        except ValueError:
            print('Marker opacity set: {} ; Invalid, set to 1.0 be default.'.format(marker_opacity_value))
            marker_opacity_value = 1.0

    return marker_opacity_value


def get_soap_spheres(data, at, atom_in_conifg_id):
    if data['mode'] != 'atomic':
        return []

    # displaced by CoM as well as the whole viewer
    # I now just moved the box and the marker, cause at_json then directly works in both modes
    pos = at.get_positions()[atom_in_conifg_id] - at.get_center_of_mass()
    pos_dict = {'x': pos[0], 'y': pos[1], 'z': pos[2]}

    shapes = [{'type': 'Sphere', "color": "gray",
               "center": pos_dict,
               "radius": data['soap_cutoff_radius'], 'wireframe': True},
              {'type': 'Sphere', "color": "green",
               "center": pos_dict,
               "radius": data['marker_radius']}
              ]
    return shapes


def construct_3d_view_data(data, point_index, periodic_repetition_str, skip_soap=False):
    # get the ids to specify the atom in the atoms_list
    config_id = data['system_index'][point_index]
    atom_in_conifg_id = data['atom_index_in_systems'][point_index]

    at_json = data['atoms_list_json'][config_id]
    at_ase = json2atoms(at_json)
    at_ase = make_periodic_ase_at(at_ase, periodic_repetition_str)

    # soap spheres and cell frame
    shapes = []
    if not skip_soap:
        shapes += get_soap_spheres(data, at_ase, atom_in_conifg_id)
    shapes += get_periodic_box_shape_dict(at_ase)

    # colour and size of the atoms in the viewer
    styles = return_atom_list_style_for_3d_view(at_ase)

    # model data: the atoms in the format that is understood by the 3D viewer
    model_data = json.loads(ase2json(at_ase))

    viewer_data = dict(styles=styles, shapes=shapes, modelData=model_data)
    return viewer_data


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

    # layout
    app.layout = html.Div(className='app-body',
                          children=[
                              # storage of the data in the application
                              dcc.Store(id='app-memory', data=data, storage_type='session'),

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
                                              dash_bio.Molecule3dViewer(id='3d-viewer', styles={}, shapes={},
                                                                        modelData={})
                                          ]))])
                          ])

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
    df = build_dataframe_features(atoms_list, mode=mode)
    system_index = None
    atom_index_in_systems = None
    if mode == 'atomic':
        system_index = df['system_ids']
        atom_index_in_systems = df['atomic_numbers']
        df.drop(['atomic_numbers', 'system_ids'], axis=1, inplace=True)

    if verbose:
        print('New Dataframe\n', df.head())

    at_list_json = [ase2json(at) for at in atoms_list]

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


def make_periodic_ase_at(ase_at, periodic_repetition_str='(0,1) (0,1) (0,1)'):
    cell = ase_at.get_cell()

    if periodic_repetition_str is not None and periodic_repetition_str != '(0,1) (0,1) (0,1)':
        # get the number of repetitions and the start+end of them
        x_rep, y_rep, z_rep = periodic_repetition_str.split(' ')
        x_rep = [int(x) for x in x_rep[1:-1].split(',')]
        x_multi = x_rep[1] - x_rep[0]
        y_rep = [int(y) for y in y_rep[1:-1].split(',')]
        y_multi = y_rep[1] - y_rep[0]
        z_rep = [int(z) for z in z_rep[1:-1].split(',')]
        z_multi = z_rep[1] - z_rep[0]

        # shift_cell = atoms_current.get_center_of_mass()
        atoms_supercell = deepcopy(ase_at) * np.array([x_multi, y_multi, z_multi])

        # shift correctly, we need to correct for the viewers automatic com centering
        new_positions = np.array([x + (cell[0] * x_rep[0] + cell[1] * y_rep[0] + cell[2] * z_rep[0]) for x in
                                  atoms_supercell.get_positions()])
        atoms_supercell.set_positions(new_positions)
        atoms_supercell.set_cell(cell)

        return atoms_supercell
    else:
        return ase_at
