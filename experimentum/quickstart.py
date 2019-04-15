# -*- coding: utf-8 -*-
"""Generate needed files and folders to get up and running.

In order to create all needed files and folders *(including config and migrations)*
the experimentum framework contains a quickstart command. Just run ``experimentum-quickstart``
and answer the questions.

You can also add a different root path with the ``--root`` option, e.g.::

    experimentum-quickstart --root example
"""
from __future__ import print_function
import sys
import os
import inflection
import datetime
from time import sleep
from termcolor import colored
from experimentum import __version__
from experimentum.cli import get_input
from experimentum.files import create_config_file, create_folder, create_from_stub


# Some default constants
APP = 'experimentum'
VERSION = __version__.__version__
ROOT = '.'


def _create_migration(path, name, upgrade, down):
    """Create a migration file.

    Args:
        path (str): Path to migrations folder.
        name (str): Name of Migration
        upgrade (str): Up method content
        down (str): down method content
    """
    revision = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = "{}/{}_{}.py".format(os.path.join(ROOT, path), revision, name.lower())
    attrs = {
        'migration': inflection.camelize(name),
        'name': name,
        'revision': revision,
        'up': upgrade,
        'down': down
    }
    create_from_stub('Migration.stub', filename, attrs)


def _create_repository(path, name, table, attributes, nullable=None, relationships=None):
    # Relationships and Imports
    relationships = relationships if relationships is not None else {}
    nullable = nullable if nullable is not None else []
    imports = []
    relations_data = []
    for attr, repo in relationships.items():
        relations_data.append("        '{}': [{}]".format(attr, repo))
        imports.append('from {0}.{1} import {1}'.format(os.path.basename(path), repo))

    if len(relations_data):
        relationships = '{\n%s\n    }' % '\n'.join(relations_data)
        imports = '\n' + '\n'.join(imports)
    else:
        relationships = '{}'
        imports = ''

    # other attrs
    filename = "{}/{}.py".format(os.path.join(ROOT, path), name)
    attrs = {
        'name': name,
        'table': table,
        'imports': imports,
        'relationships': relationships,
        'kwargs': ', '.join(
            map(lambda attr: '{}{}'.format(attr, '=None' if attr in nullable else ''), attributes)
        ),
        'set_attr': '\n        '.join(map('self.{0} = {0}'.format, attributes))
    }

    # print(attrs)
    create_from_stub('Repository.stub', filename, attrs)


def main():
    """Generate needed files and folders to get up and running."""
    # Set Root
    global ROOT
    if len(sys.argv) == 3 and sys.argv[1] == '--root':
        ROOT = os.path.join('.', sys.argv[2])

    # Welcome Text
    print(colored('Welcome to the {} {} quickstart utility.'.format(APP, VERSION), attrs=['bold']))
    print('\nPlease enter values for the following settings (just press Enter to')
    print('accept a default value, if one is given in brackets)\n')
    print(colored('Selected root path: {}\n'.format(ROOT), attrs=['bold']))

    # Get Config from User
    _folders = ['config', 'migrations', 'repositories', 'experiments', 'logs']
    folders = {
        key: get_input('Enter the name of the {} folder'.format(key), key) for key in _folders
    }
    app = {}
    app['name'] = get_input('Enter the name of the app')
    app['desc'] = get_input('Enter the description of the app', '')
    app['prog'] = get_input('Enter the name of the program', 'main.py')

    # Prepare and create folders
    print(colored('\nCreating folders ...', 'cyan'))
    for key, folder in folders.items():
        with_init = True if key == 'experiments' or key == 'repositories' else False
        create_folder(ROOT, folder, with_init=with_init)

    # Create Entry Point
    print(colored('Creating main entry point ...', 'cyan'))
    attrs = {
        'klass': inflection.camelize(app['name'].replace(' ', '_')),
        'name': app['name'],
        'config_path': folders['config']
    }
    create_from_stub('App.stub', os.path.join(ROOT, app['prog']), attrs)

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
        },
        'experiments': {'path': folders['experiments']}
    }
    storage_cfg = {
        'datastore': {
            'drivername': 'sqlite',
            'database': '{}.db'.format(app['name']),
            'username': None,
            'password': None,
            'host': None,
            'port': None
        },
        'migrations': {'path': folders['migrations']},
        'repositories': {'path': folders['repositories']}
    }

    create_config_file(ROOT, folders['config'], 'app.json', app_cfg)
    create_config_file(ROOT, folders['config'], 'storage.json', storage_cfg)

    # Create Migrations
    print(colored('Creating migrations ...', 'cyan'))
    _create_migration(
        folders['migrations'],
        'create_experiments',
        upgrade="""with self.schema.create('experiments') as table:
            table.increments('id')
            table.primary('id')
            table.string('name', 75)
            table.datetime('start')
            table.datetime('finished').nullable()
            table.string('config_file').nullable()
            table.text('config_content').nullable()""",
        down="self.schema.drop_if_exists('experiments')"
    )
    sleep(1)
    _create_migration(
        folders['migrations'],
        'create_testcase',
        upgrade=r"""with self.schema.create('testcases') as table:
            table.increments('id')
            table.primary('id')
            table.increments('experiment_id')
            table.foreign('experiment_id')\
                .references('id').on('experiments')\
                .on_delete('cascade')\
                .on_update('cascade')""",
        down="self.schema.drop_if_exists('testcases')"
    )
    sleep(1)
    _create_migration(
        folders['migrations'],
        'create_performance',
        upgrade=r"""with self.schema.create('performance') as table:
            table.big_increments('id')
            table.primary('id')
            table.string('label', 75)
            table.small_integer('level')
            table.string('type', 25)
            table.float('time')
            table.float('memory')
            table.float('peak_memory')
            table.integer('test_id')
            table.foreign('test_id')\
                .references('id').on('testcases')\
                .on_delete('cascade')\
                .on_update('cascade')""",
        down="self.schema.drop_if_exists('performance')"
    )

    # Create Repositories
    print(colored('Creating repositories ...', 'cyan'))
    _create_repository(
        folders['repositories'],
        'ExperimentRepository',
        'experiments',
        attributes=['name', 'config_file', 'start', 'config_content', 'finished'],
        nullable=['finished', 'config_content'],
        relationships={'tests': 'TestCaseRepository'}
    )
    _create_repository(
        folders['repositories'],
        'TestCaseRepository',
        'testcases',
        attributes=['iteration', 'experiment_id'],
        nullable=['experiment_id'],
        relationships={'performances': 'PerformanceRepository'}
    )
    _create_repository(
        folders['repositories'],
        'PerformanceRepository',
        'performance',
        attributes=['label', 'level', 'type', 'time', 'memory', 'peak_memory'],
    )

    # Done
    print(colored('Done.', 'yellow'))


if __name__ == '__main__':
    main()
