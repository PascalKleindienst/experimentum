"""Main entry point of the framework.

Sets up the framework and runs the experiments and lets you customize/extend
the behavior of the framework.

Register new commands with the :py:meth:`.App.register_commands` method.
It should return a dictionary where the keys are names of the commands and
the values are the command handlers. The command handlers must either be
derived from :py:class:`.AbstractCommand` or a function with the decorator
:py:func:`.AbstractCommand.command`. Example return::

    {
        'foo': FooCommand,
        'bar': BarCommand
    }

Add more aliases or change aliases with the :py:meth:`.App.register_aliases` method.
To create a new instance of an aliased class just run the :py:meth:`.App.make` method::

    class MyDerivedApp(App):
        def register_aliases(self):
            super(MyDerivedApp, self).register_aliases()  # register default aliases

            # register alias 'foo' and pass all args and kwargs when called with make
            self.aliases['foo'] = lambda *args, **kwargs: Foo(*args, **kwargs)

    ...

    # create a new instance of Foo and pass the args to it.
    foo = app.make('foo', 42, bar='foobar')


"""
from __future__ import print_function
import os
import sys
import logging
import logging.handlers
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from experimentum.cli import print_failure
from experimentum.Config import Config, Loader
from experimentum.Commands import CommandManager, MigrationCommand, ExperimentsCommand
from experimentum.Experiments import Experiment
from experimentum.Storage.AbstractRepository import RepositoryLoader
from experimentum.Storage.Migrations import Migrator, Blueprint, Schema
from experimentum.Storage.SQLAlchemy import Store, Repository


def _path_join(root, path):
    """Join root with relative path.

    Args:
        root (str): Root path
        path (str): relative path to root

    Returns:
        str: realpath
    """
    return os.path.realpath(os.path.join(root, path))


class App(object):

    """Main entry point of the framework.

    Attributes:
        config_path (str): Defaults to ``.``. Path to config files.
        base_repository (AbstractRepository): Defaults to ``Repository``. Repository Base Class
        name (str): Name of the app.
        root (str): Root Path of the app.
        config (Config): Config Manager.
        log (logging.Logger): Logger.
        store (AbstractStore): Data Store.
        aliases (dict): Dictionary of aliases and factory functions.
    """
    config_path = '.'
    base_repository = Repository

    def __init__(self, name, root):
        """Bootstrap the app framework.

        Args:
            name (str): Name of the App.
        """
        self.name = name
        self.root = os.path.dirname(root)
        self.log = logging.getLogger('experimentum')
        self.config = Config()
        self.store = None
        self.aliases = {}
        self.bootstrap()

    def bootstrap(self):
        """Bootstrap the app, i.e. setup config and logger."""
        # Load Config
        loader = Loader(_path_join(self.root, self.config_path), self.config)
        loader.load_config_files()

        # Add experiments and repo folders to path
        paths = [
            self.config.get('app.experiments.path', 'experiments'),
            self.config.get('storage.repositories.path', 'repositories')
        ]
        for path in paths:
            sys.path.insert(0, os.path.abspath(_path_join(self.root, path)))

        # Setup logger
        self._set_logger()
        self.log.info('Bootstrap App')

        # Setup Datastore
        default_db = {'drivername': 'sqlite', 'database': 'experimentum.db'}
        database = self.config.get('storage.datastore', default_db)

        if database['drivername'] == 'sqlite':  # Absolute db path based on root
            database['database'] = _path_join(self.root, database['database'])

        self.setup_datastore(database)

        # Load and map Repositories
        self.repositories = RepositoryLoader(self, self.base_repository, self.store)
        self.repositories.load()

        # Aliases
        self.register_aliases()

        # Register commands
        self.log.info('Register Commands')
        self.cmd_manager = CommandManager(
            self,
            self.config.get('app.prog', 'app'),
            self.config.get('app.description', '')
        )
        self._add_commands()

        # save app instance
        # app(self)

    def setup_datastore(self, datastore):
        """Set up the data store."""
        self.log.info('Setup Data Store')
        self.store = Store(self)
        self.store.set_engine(create_engine(URL(**datastore)))

    def make(self, alias, *args, **kwargs):
        """Create an instance of an aliased class.

        Args:
            alias (str): Name of class alias.

        Raises:
            Exception: if the alias does not exists.

        Returns:
            object: Instance of the aliased class
        """
        klass = self.aliases.get(alias, None)

        if klass is None:
            print_failure("Class with alias '{}' does not exist.".format(alias), 1)

        return klass(*args, **kwargs)

    def run(self):
        """Run the app."""
        self.cmd_manager.dispatch()
        self.log.info('Run App')

    def register_commands(self):
        """Register custom cli commands.

        Returns:
            dict: commands to register
        """
        return {}

    def register_aliases(self):
        """Register aliases for classes."""
        self.log.info('Register Aliases')

        migration_path = self.config.get('storage.migrations.path', 'migrations')
        experiments_path = self.config.get('app.experiments.path', 'experiments')

        self.aliases = {
            'experiment':
                lambda name: Experiment.load(self, _path_join(self.root, experiments_path), name),
            'migrator':
                lambda: Migrator(_path_join(self.root, migration_path), self),
            'store': lambda: self.store,
            'schema': lambda: Schema(self),
            'blueprint': lambda *args, **kwargs: Blueprint(*args, **kwargs),
        }

    def _add_commands(self):
        """Add Commands to the command manager."""
        commands = self._commands()
        user_commands = self.register_commands()

        if any(user_commands):
            commands.update(user_commands)

        for name, cmd in commands.items():
            self.log.debug('Adding Command {}'.format(name))
            self.cmd_manager.add_command(name, cmd)

    @classmethod
    def _commands(cls):
        """Register default commands.

        Returns:
            dict: Default commands
        """
        return {
            'experiments:run': ExperimentsCommand.run,
            'migration:status': MigrationCommand.status,
            'migration:refresh': MigrationCommand.refresh,
            'migration:up': MigrationCommand.up,
            'migration:down': MigrationCommand.down,
            'migration:make': MigrationCommand.make,
        }

    def _set_logger(self):
        """Set up the logger and its handlers."""
        # Set log level
        levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        level = levels.get(
            self.config.get('app.logging.level', 'info'), logging.NOTSET
        )
        self.log.setLevel(level)

        # Add filehandler and Formatter
        name = self.config.get(
            'app.logging.filename',
            '{name}.log'
        ).format(name=self.name).lower()

        filename = '{}/{}'.format(
            os.path.realpath(_path_join(self.root, self.config.get('app.logging.path', '.'))),
            name
        )
        filehandler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=self.config.get('app.logging.max_bytes', 1024 * 1024),  # default to 1MB
            backupCount=self.config.get('app.logging.backup_count', 10),
            mode='a+'
        )
        filehandler.setLevel(level)
        filehandler.setFormatter(logging.Formatter(self.config.get(
            'app.logging.format',
            '[%(asctime)s] - [%(levelname)s] - [%(module)s] - %(message)s'
        )))
        self.log.addHandler(filehandler)
