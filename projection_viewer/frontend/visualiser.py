import json

import numpy as np
from ase.data import covalent_radii
from ase.data.colors import jmol_colors

from projection_viewer.utils import get_hex_color, json2atoms, make_periodic_ase_at, ase2json


def get_style_config_dict(title='Example', height_viewer=500, width_viewer=500, **kwargs):
    config_dict = dict(title=title,
                       height_viewer=height_viewer,
                       width_viewer=width_viewer,
                       **kwargs)

    return config_dict


def get_periodic_box_shape_dict(atoms_ase):
    # check whether a periodic box is needed to be drawn, and return it as a shape if needed
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


def return_atom_list_style_for_3d_view(ase_atoms):
    dict_style = {}
    for i, at in enumerate(ase_atoms):
        hex_color = get_hex_color([int(x * 255) for x in jmol_colors[ase_atoms.get_atomic_numbers()[i]]])
        # hex_color = '#%02x%02x%02x' % (c_rgb[0], c_rgb[1], c_rgb[2])
        dict_style[str(i)] = {"color": hex_color, "visualization_type": "sphere",
                              "radius": covalent_radii[ase_atoms.get_atomic_numbers()[i]]}
    return dict_style


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