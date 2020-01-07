import ase.io
import numpy as np
import womblepy.testing
import womblepy.utils


def ener_errors(CP2K_filename, GAP_filename):
    e0_byhand = {'H': -13.69926302469624,
                 'C': -146.4190915732722,
                 'O': -432.29848070683704}

    ########################
    # Reading the data
    ########################

    at_list_cp2k = ase.io.read(CP2K_filename, ':')
    at_list_gap = ase.io.read(GAP_filename, ':')

    # take energies from the atoms lists
    energy_cp2k_array = womblepy.testing.extract_energies(at_list_cp2k, 'energy', e0=e0_byhand)
    energy_gap_array = womblepy.testing.extract_energies(at_list_gap, 'energy', e0=e0_byhand)

    # remove single atoms
    deleted = np.zeros((energy_cp2k_array.shape[0],), dtype=bool)
    remaining_at_list_gap = []
    for i, at in enumerate(at_list_gap):
        if len(at) == 1:
            deleted[i] = True
        else:
            remaining_at_list_gap.append(at)
    # now remove these for the rest of the work
    energy_cp2k_array = energy_cp2k_array[~deleted]
    energy_gap_array = energy_gap_array[~deleted]

    for i, at in enumerate(remaining_at_list_gap):
        at.info['gap_energy'] = energy_gap_array[i]
        at.info['cp2k_energy'] = energy_cp2k_array[i]
        at.info['abs_error'] = np.abs(energy_cp2k_array[i] - energy_gap_array[i])
        at.info['index'] = i

    fn = 'processed.xyz'
    ase.io.write(fn, remaining_at_list_gap)
    return fn
