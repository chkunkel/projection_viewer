def get_features_molecular(feature, atoms):
    "Returns a list with the molecular feature for all geometries in `atoms`"
    return [atoms_i.info[feature] for atoms_i in atoms]

def get_features_atomic(feature, atoms, consider_species):
    "Returns a list with the atomic features for the `consider_species` for all geometries in `atoms`"
    features = []
    for atoms_i in atoms:
        features.extend([feature_i for feature_i, symbol_i in zip(atoms_i.arrays[feature], atoms_i.get_chemical_symbols()) if symbol_i in consider_species])
    return features

def get_atomic_numbers(atoms, consider_species):
    "Returns a list with the atomic numbers for the `consider_species` for all geometries in `atoms`"
    atomic_numbers = []
    for atoms_i in atoms:
        atomic_numbers.extend([number for number, symbol in zip(atoms_i.get_atomic_numbers(), atoms_i.get_chemical_symbols()) if symbol in consider_species])
    return atomic_numbers

