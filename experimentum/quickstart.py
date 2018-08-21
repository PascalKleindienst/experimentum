# -*- coding: utf-8 -*-
"""Generate needed files and folders to get up and running.

In order to create all needed files and folders *(including config and migrations)*
the experimentum framework contains a quickstart command. Just run ``experimentum-quickstart``
and answer the questions.

You can also add a different root path with the ``--root`` option, e.g.::

    experimentum-quickstart --root example
"""
from __future__ import print_function
import six
import sys
import os
import json
import inflection
import datetime
from termcolor import colored
from experimentum import __version__


# Some default constants
APP = 'experimentum'
VERSION = __version__.__version__
ROOT = '.'
MIGRATION = """from experimentum.Storage.Migrations import Migration


class {migration}(Migration):

    \"\"\"Create the {name} migration.\"\"\"
    revision = '{revision}'

    def up(self):
        \"\"\"Run the migrations.\"\"\"
        {up}

    def down(self):
        \"\"\"Revert the migrations.\"\"\"
        {down}
"""
ENTRY_POINT = """# -*- coding: utf-8 -*-
from experimentum.Experiments import App


class {klass}(App):

    \"\"\"Main Entry Point of the Framework.

    Args:
        config_path {{string}} -- Path to config files (default: {{'.'}})
    \"\"\"
    config_path = '{config_path}'

    def register_commands(self):
        \"\"\"Register Custom Commands.

        Returns:
            dict -- {{ Name of command : Command Handler }}
        \"\"\"
        return {{}}


if __name__ == '__main__':
    app = {klass}('{name}')
    app.run()
"""


def _get_input(msg, default=None):
    """Get the user input.

    Args:
        msg (str): Message
        default (object, optional): Default to None. Default value if nothing is entered

    Returns:
        object: User Input
    """
    # Default value if skipped
    if default is not None:
        return six.moves.input(colored("› {} [{}]: ".format(msg, default), 'green')) or default

    # Required input
    value = six.moves.input(colored("› {}: ".format(msg), 'green'))
    while value is '':
        print(colored("× Please specify a value!", 'red'))
        value = six.moves.input(colored("› {}: ".format(msg), 'green'))

    return value


def _create_folder(path):
    """Create a folder if it does not exist.

    Args:
        path (str): folder path
    """
    path = os.path.realpath(os.path.join(ROOT, path))
    if os.path.exists(path) is False:
        os.makedirs(path)


def _create_config_file(path, name, data):
    """Create a config file and fill it with data.

    Args:
        path (str): Path to config folder
        name (str): Name of the config file
        data (object): Config Data
    """
    path = os.path.realpath(os.path.join(ROOT, path))
    with open(os.path.join(path, name), 'w+') as cfg:
        json.dump(data, cfg, sort_keys=False, indent=4, separators=(',', ': '))


def _create_migration(path, name, up, down):
    """Create a migration file.

    Args:
        path (str): Path to migrations folder.
        name (str): Name of Migration
        up (str): Up method content
        down (str): down method content
    """
    migration = inflection.camelize(name)
    revision = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = "{}/{}_{}.py".format(os.path.join(ROOT, path), revision, name.lower())

    with open(filename, 'w+') as file:
        file.write(MIGRATION.format(
            migration=migration,
            name=name,
            revision=revision,
            up=up,
            down=down
        ))


def main():
    """Generate needed files and folders to get up and running."""
    # Set Root
    global ROOT
    if len(sys.argv) is 3 and sys.argv[1] == '--root':
        ROOT = os.path.join('.', sys.argv[2])

    # Welcome Text
    print(colored('Welcome to the {} {} quickstart utility.'.format(APP, VERSION), attrs=['bold']))
    print('\nPlease enter values for the following settings (just press Enter to')
    print('accept a default value, if one is given in brackets)\n')

    print(colored('Selected root path: {}\n'.format(ROOT), attrs=['bold']))

    # Get Config from User
    folders = {'config': '', 'migrations': ''}
    app = {'name': '', 'desc': '', 'prog': ''}

    folders['config'] = _get_input('Enter the name of the config folder', 'config')
    folders['migrations'] = _get_input('Enter the name of the migrations folder', 'migrations')
    folders['logs'] = _get_input('Enter the name of the log folder', 'logs')
    app['name'] = _get_input('Enter the name of the app')
    app['desc'] = _get_input('Enter the description of the app', '')
    app['prog'] = _get_input('Enter the name of the program', 'main.py')

    # Prepare and create folders
    print(colored('\nCreating folders ...', 'cyan'))
    for folder in folders.values():
        _create_folder(folder)

    # Create Entry Point
    print(colored('Creating main entry point ...', 'cyan'))
    with open(os.path.join(ROOT, app['prog']), 'w+') as main:
        main.write(ENTRY_POINT.format(**{
            'klass': inflection.camelize(app['name'].replace(' ', '_')),
            'name': app['name'],
            'config_path': folders['config']
        }))

    # Creat config items
    print(colored('Creating config files ...', 'cyan'))
    app_cfg = {
        'prog': app['prog'],
        'description': app['desc'],
        'logging': {
            'level': 'info',
            'format': '[%(asctime)s] - [%(levelname)s] - [%(module)s] - %(message)s',
            'filename': '{}.log'.format(app['name'].replace(' ', '_').lower()),
            'path': folders['logs'],
            'max_bytes': 1024*1024,
            'backup_count': 10
        }
    }
    storage_cfg = {
        'datastore': {
            'drivername': 'sqlite',
            'database': 'experimentum.db',
            'username': None,
            'password': None,
            'host': None,
            'port': None
        },
        'migrations': {
            'path': folders['migrations']
        }
    }

    _create_config_file(folders['config'], 'app.json', app_cfg)
    _create_config_file(folders['config'], 'storage.json', storage_cfg)

    # Create Migrations
    _create_migration(
        folders['migrations'],
        'create_experiments',
        up="""with self.schema.create('experiments') as table:
            table.increments('id')
            table.primary('id')""",
        down="self.schema.drop_if_exists('experiments')"
    )

    # Done
    print(colored('Done.', 'yellow'))


if __name__ == '__main__':
    main()
