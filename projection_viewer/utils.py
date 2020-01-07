import json
import os
from copy import deepcopy

import ase
import ase.io
import numpy as np
import pandas as pd


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


# '''
# This is taken from rtools.helpers.converters
# Courtesy of Simon Rittmeyer and Christoph Schober
# We didn't want to steal it, but wanted to avoid a further dependency
# '''
#
# try:
#     import StringIO as io
# except ImportError:
#     import io
#
#
# def ase2xyz(atoms):
#     """
#     Prepare a XYZ string from an ASE atoms object.
#     """
#     # Implementation detail: If PBC should be implemented, the
#     # write to xyz needs to be changed to include cell etc.
#     if any(atoms.get_pbc()):
#         raise RuntimeError("Detected PBCs. Not supported (yet)!")
#     num_atoms = len(atoms)
#     types = atoms.get_chemical_symbols()
#     all_atoms = zip(types, atoms.get_positions())
#     a_str = str(num_atoms) + "\n" + "\n"
#     for atom in all_atoms:
#         a_str += atom[0] + " " + " ".join([str(x) for x in atom[1]]) + "\n"
#     return a_str


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
        try:
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
        except KeyError as err:
            print('Skipping key:', err)

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


_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_asset_folder():
    # fixme: this would be nicer with finding the package data
    # print get_data('resource1/foo.txt')
    return os.path.join(_ROOT, '../assets')