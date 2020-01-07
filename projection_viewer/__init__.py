import os

import projection_viewer.backends
import projection_viewer.frontend
import projection_viewer.utils
import projection_viewer.processors

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_asset_folder():
    # fixme: this would be nicer with finding the package data
    # print get_data('resource1/foo.txt')
    return os.path.join(_ROOT, '../assets')
