"""Main Service Container and Provider.

Sets up the framework and runs the experiments and lets you customize/extend
the behavior of the framework.

Binding
-------
We can register/bind a new  alias by extending either the :py:meth:`~.App.register_aliases class`
or by directly adding the alias to the :py:attr:`~.App.aliases` dictionary. The key is the alias
name you want to register and the value is a function that returns an instance of the class::

    def register_aliases(self):
        super(MyAppClass, self).register_aliases()

        self.aliases['my_custom_api'] = lambda: API(self.store)

Additional arguments for creating a class instance may be passed when resolving. Your function
just has to add them in order to use them::

    self.aliases['my_custom_api'] = lambda name, user_id=None: API(self.store, name, user_id)

Resolving
---------
You may use the :py:meth:`~.App.make` method to resolve a class instance out of the container.
The :py:meth:`~.App.make` method accepts the alias of the class you want to resolve::

    api = self.app.make('my_custom_api')

If some of your class' dependencies are not resolvable via the app container, you may pass them
as additional args and keyword args::

    api = self.app.make('my_custom_api', foo, user_id=42)

Customizing
-----------

Commands
^^^^^^^^
Register new commands with the :py:meth:`.App.register_commands` method.
It should return a dictionary where the keys are names of the commands and
the values are the command handlers. The command handlers must either be
derived from :py:class:`.AbstractCommand` or a function with the decorator
:py:func:`.AbstractCommand.command`. Example return::

    {
        'foo': FooCommand,
        'bar': BarCommand
    }
"""
from __future__ import print_function
import os
import sys
import logging
import logging.handlers
from collections import OrderedDict
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from experimentum.cli import print_failure
from experimentum.Config import Config, Loader
from experimentum.Commands import CommandManager, MigrationCommand, ExperimentsCommand,\
    PlotCommand, WebGUICommand
from experimentum.Experiments import Experiment
from experimentum.Storage.AbstractStore import AbstractStore
from experimentum.Storage.AbstractRepository import RepositoryLoader
from experimentum.Storage.Migrations import Migrator, Blueprint, Schema
from experimentum.Storage.SQLAlchemy import Store, Repository
from experimentum.Plots import Factory
from experimentum.WebGUI import Server


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
        self.log.info('Setup Data Store')
        default_db = {'drivername': 'sqlite', 'database': 'experimentum.db'}
        database = self.config.get('storage.datastore', default_db)

        if database['drivername'] == 'sqlite' and database['database'] != '':  # Absolute db path based on root
            database['database'] = _path_join(self.root, database['database'])

        self.setup_datastore(database)

        if not isinstance(self.store, AbstractStore):
            msg = 'The "{}" Store implementation must implement the AbstractStore interface'
            print_failure(msg.format(self.store.__class__), 1)

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
        """Set up the data store.

        Args:
            datastore (dict): Datastore config.
        """
        self.store = Store(self)

        db_args = {}
        if datastore['drivername'] == 'sqlite':
            db_args['connect_args'] = {'check_same_thread': False}

        self.store.set_engine(
            create_engine(URL(**datastore), **db_args)
        )

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
        plot_factory = Factory(self)

        self.aliases = {
            'experiment':
                lambda name: Experiment.load(self, _path_join(self.root, experiments_path), name),
            'migrator':
                lambda: Migrator(_path_join(self.root, migration_path), self),
            'plot': lambda name: plot_factory.create(name),
            'store': lambda: self.store,
            'schema': lambda: Schema(self),
            'blueprint': lambda *args, **kwargs: Blueprint(*args, **kwargs),
            'server': lambda: Server(self),
            'config': lambda: Config()
        }

    def _add_commands(self):
        """Add Commands to the command manager."""
        commands = self._commands()
        user_commands = self.register_commands()

        if any(user_commands):
            commands.update(OrderedDict(sorted(user_commands.items(), key=lambda c: c[0])))

        for name, cmd in commands.items():
            self.log.debug('Adding Command {}'.format(name))
            self.cmd_manager.add_command(name, cmd)

    @classmethod
    def _commands(cls):
        """Register default commands.

        Returns:
            dict: Default commands
        """
        commands = OrderedDict()
        commands['experiments:run'] = ExperimentsCommand.run
        commands['experiments:list'] = ExperimentsCommand.status
        commands['migration:status'] = MigrationCommand.status
        commands['migration:refresh'] = MigrationCommand.refresh
        commands['migration:up'] = MigrationCommand.up
        commands['migration:down'] = MigrationCommand.down
        commands['migration:make'] = MigrationCommand.make
        commands['plot:generate'] = PlotCommand.generate
        commands['webgui'] = WebGUICommand.start

        return commands

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
