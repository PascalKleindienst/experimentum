"""Some Helper functions for creating files and folders."""
import os
import json


def create_folder(root, path, with_init=False):
    """Create a folder if it does not exist.

    Args:
        root (str): Root folder
        path (str): folder path
        with_init (bool): Add an __init__.py to folder or not
    """
    path = os.path.realpath(os.path.join(root, path))
    if os.path.exists(path) is False:
        os.makedirs(path)

    if with_init:
        with open(os.path.join(path, '__init__.py'), 'w+') as filehandler:
            filehandler.write('')


def create_config_file(root, path, name, data):
    """Create a config file and fill it with data.

    Args:
        root (str): Root folder
        path (str): Path to config folder
        name (str): Name of the config file
        data (object): Config Data
    """
    path = os.path.realpath(os.path.join(root, path))
    with open(os.path.join(path, name), 'w+') as cfg:
        json.dump(data, cfg, sort_keys=False, indent=4, separators=(',', ': '))


def create_from_stub(stubfile, filename, attrs):
    """Create a new file from a stub.

    Args:
        stubfile (str): Name of stub file in _stubs folder
        filename (str): Filename to create (with path)
        attrs (dict): Attributes to pass to stub
    """
    # Load Stub file
    stub = ''
    with open(os.path.join(os.path.dirname(__file__), '_stubs', stubfile), 'r') as filehandler:
        stub = filehandler.read()

    # Create new file based on stub
    with open(filename, 'w+') as filehandler:
        filehandler.write(stub.format(**attrs))
