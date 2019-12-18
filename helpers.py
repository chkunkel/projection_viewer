import numpy as np
import pandas as pd
from ase.data import covalent_radii
from ase.data.colors import jmol_colors


def get_features_molecular(feature, atoms):
    "Returns a list with the molecular feature for all geometries in `atoms`"
    return [atoms_i.info[feature] for atoms_i in atoms]


def get_features_atomic(feature, atoms):
    "Returns a list with the atomic features for all geometries in `atoms`"
    features = []
    for atoms_i in atoms:
        features.extend(
            [feature_i for feature_i, symbol_i in zip(atoms_i.arrays[feature], atoms_i.get_chemical_symbols())])
    return features


def get_atomic_numbers(atoms):
    "Returns a list with the atomic numbers for all geometries in `atoms`"
    atomic_numbers = []
    for atoms_i in atoms:
        atomic_numbers.extend(
            [number for number, symbol in zip(atoms_i.get_atomic_numbers(), atoms_i.get_chemical_symbols())])
    return atomic_numbers


def ase2json(atoms_ase):
    atoms_ase.translate(atoms_ase.get_center_of_mass() * -1)
    json_str = '{"atoms": ['
    for i, pos in enumerate(atoms_ase.get_positions()):
        elem = str(atoms_ase.get_chemical_symbols()[i])
        json_str += '{"name":"' + elem + '","chain":"A","residue_index":0,"residue_name":"A", "serial": "' + str(
            i) + '","element":"' + elem + '", "positions":' + str(list(pos)) + '}'
        if not i == len(atoms_ase) - 1:
            json_str += ","
    json_str += '], "bonds":[]}'

    return json_str


def get_hex_color(c_rgb):
    return '#%02x%02x%02x' % (c_rgb[0], c_rgb[1], c_rgb[2])


def return_style(atoms_id, default=-1):
    dict_style = {}
    for i, at in enumerate(atoms_id):
        hex_color = get_hex_color([int(x * 255) for x in jmol_colors[atoms_id.get_atomic_numbers()[i]]])
        # hex_color = '#%02x%02x%02x' % (c_rgb[0], c_rgb[1], c_rgb[2])
        dict_style[str(i)] = {"color": hex_color, "visualization_type": "sphere",
                              "radius": covalent_radii[atoms_id.get_atomic_numbers()[i]]}
    return dict_style


# check whether a periodic box is needed to be drawn, and return it as a shape if needed
def get_periodic_box_shape_dict(atoms_ase):
    # so far we only show a box when it is 3d periodic
    if not np.any(atoms_ase.get_cell_lengths_and_angles()[0:3] > 0): return []

    #point0 = np.array([0.0, 0.0, 0.0])
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

# rm
# import json
# import six.moves.urllib.request as urlreq
# from six import PY3
# model_data = urlreq.urlopen('https://raw.githubusercontent.com/Autodesk/molecule-3d-for-react/master/example/js/bipyridine_model_data.js').read()
# model_data=str(model_data)
# model_data = model_data.replace("\\n", """""").split("default")[1].split(";")[0]
# print(model_data)
# modelData = json.loads(model_data)
# modelData.pop("bonds")

#  'https://raw.githubusercontent.com/plotly/dash-bio-docs-files/master/' +
#    'mol3d/model_data.js'


# {"name": "HD21", "chain": "A", "positions": [-13.031, 4.622, 2.311], "residue_index": 11, "element": "H", "residue_name": "ASN11", "serial": 110}, {"name": "HD22", "chain": "A", "positions": [-13.154, 6.114, 3.177], "residue_index": 11, "element": "H", "residue_name": "ASN11", "serial": 111}
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
