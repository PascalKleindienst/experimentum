from experimentum.cli import print_failure
import glob
import os
import imp
import re


def find_files(root, path, search=None, remove='.py'):
    """Find files in a folder (except _*.py files).

    Can also search for specific filenames (case ignored).

    Args:
        root (str): Root Path
        path (str): Path to folder
        search (str, optional): Defaults to None. Filename to search for
        remove (str, optional): Defaults to '.py'. Exclude from filename comparison

    Returns:
        list: List of filenames
    """
    regex = re.compile(remove, re.IGNORECASE)
    files = glob.glob(os.path.join(root, path, '[!_]*.py'))

    if search:
        files = list(filter(
            lambda file: search.lower() == re.sub(regex, '', os.path.basename(file)).lower(),
            files
        ))

    return files


def get_basenames(root, path, remove='.py'):
    """Get file basenames of a folder.

    Args:
        root (str): Root path
        path (str): Path to folder
        remove (str, optional): Defaults to '.py'. Part to remove from filename.

    Returns:
        list: list of names
    """
    regex = re.compile(remove, re.IGNORECASE)
    files = find_files(root, path, remove=remove)

    return list(map(
        lambda file: re.sub(regex, '', os.path.basename(file)),
        files
    ))


def load_class(src, module, subclass=None):
    """Try to load a class from a module.

    Args:
        src (str): Source file
        module (str): Module name
        subclass (object, optional): Defaults to None. Object the class needs to be derived from

    Returns:
        object: loaded class
    """
    with open(src, 'rb') as filehandler:
        # try to load class from module
        try:
            mod = imp.load_source(module, src, filehandler)
            klass = getattr(mod, os.path.basename(src)[:-3])
        except Exception as exc:
            print_failure('Could not load file: %s' % str(exc), exit_code=2)

        # Check if class is derived from subclass
        if subclass and issubclass(klass, subclass) is False:
            msg = '{} must be derived from the {}.{} class'.format(
                klass.__name__,
                subclass.__module__,
                subclass.__name__
            )
            print_failure(msg, exit_code=3)

        return klass
