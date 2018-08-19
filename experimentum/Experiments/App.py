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
from experimentum.Config import Config, Loader
from experimentum.Commands import CommandManager, MigrationCommand, print_failure
from experimentum.Storage.Migrations import Migrator, Blueprint, Schema
from experimentum.Storage.SQLAlchemy import Store


class App(object):

    """Main entry point of the framework.

    Attributes:
        config_path (string): Defaults to ``.``. Path to config files.
        name (string): Name of the app.
        config (Config): Config Manager.
        log (logging.Logger): Logger.
        store (AbstractStore): Data Store.
        aliases (dict): Dictionary of aliases and factory functions.
    """
    config_path = '.'

    def __init__(self, name):
        """Bootstrap the app framework.

        Args:
            name (string): Name of the App.
        """
        self.name = name
        self.bootstrap()

    def bootstrap(self):
        """Bootstrap the app, i.e. setup config and logger."""
        # Load Config
        self.config = Config()
        loader = Loader(os.path.realpath(self.config_path), self.config)
        loader.load_config_files()

        # Setup logger
        self._set_logger()
        self.log.info('Bootstrap App')

        # Setup Datastore
        self.setup_datastore()

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

    def setup_datastore(self):
        """Set up the data store."""
        self.log.info('Setup Data Store')
        default_db = {'drivername': 'sqlite', 'database': 'experimentum.db'}
        engine = create_engine(URL(**self.config.get('storage.datastore', default_db)))
        self.store = Store(self)
        self.store.set_engine(engine)

    def make(self, alias, *args, **kwargs):
        """Create an instance of an aliased class.

        Args:
            alias (string): Name of class alias.

        Raises:
            Exception: if the alias does not exists.

        Returns:
            object: Instance of the aliased class
        """
        klass = self.aliases.get(alias, None)

        if klass is None:
            msg = "Class with alias '{}' does not exist.".format(alias)
            self.log.critical(msg)
            print_failure(msg)
            sys.exit(1)

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

        self.aliases = {
            'migrator':
                lambda: Migrator(self.config.get('storage.migrations.path', 'migrations'), self),
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

    def _commands(self):
        """Register default commands.

        Returns:
            dict: Default commands
        """
        return {
            'migration:status': MigrationCommand.status,
            'migration:refresh': MigrationCommand.refresh,
            'migration:up': MigrationCommand.up,
            'migration:down': MigrationCommand.down,
            'migration:make': MigrationCommand.make,
        }

    def _set_logger(self):
        """Set up the logger and its handlers."""
        self.log = logging.getLogger('experimentum')

        # Set log level
        LEVELS = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        level = LEVELS.get(
            self.config.get('app.logging.level', 'info'), logging.NOTSET
        )
        self.log.setLevel(level)

        # Add filehandler and Formatter
        name = self.config.get(
            'app.logging.filename',
            '{name}.log'
        ).format(name=self.name).lower()

        filename = '{}/{}'.format(
            os.path.realpath(self.config.get('app.logging.path', '.')),
            name
        )
        fh = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=self.config.get('app.logging.max_bytes', 1024 * 1024),  # default to 1MB
            backupCount=self.config.get('app.logging.backup_count', 10),
            mode='a+'
        )
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(self.config.get(
            'app.logging.format',
            '[%(asctime)s] - [%(levelname)s] - [%(module)s] - %(message)s'
        )))
        self.log.addHandler(fh)
