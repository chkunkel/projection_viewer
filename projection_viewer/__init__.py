import os

import projection_viewer.helpers

_ROOT = os.path.abspath(os.path.dirname(__file__))
# fixme: this would be nicer with finding the package data
# print get_data('resource1/foo.txt')


def get_asset_folder():
    return os.path.join(_ROOT, '../assets')


