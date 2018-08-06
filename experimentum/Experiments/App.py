from __future__ import print_function
import os
import sys
import logging
import logging.handlers
from experimentum.Config import Config, Loader
from experimentum.Commands import CommandManager, MigrationCommand, print_failure
from experimentum.Storage.Migrations import Migrator

_app = None


def app(app=None):
    """Singleton helper for app.

    Keyword Arguments:
        app {App} -- Set current app (default: {None})

    Returns:
        App
    """
    global _app
    if app:
        _app = app
    return _app


class App(object):

    """Main entry point of the framework.

    Arguments:
        config_path {string} -- Path to config files (default: {'.'})
        name {string} -- Name of the app
        config {Config} -- Config Manager
        log {logging.Logger} -- Logger
        aliases {dict} -- Dictionary of aliases and factory functions
    """
    config_path = '.'

    def __init__(self, name):
        """Bootstrap the app framework.

        Arguments:
            name {string} -- Name of the App
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
        app(self)

    def make(self, alias):
        """Create an instance of an aliased class.

        Arguments:
            alias {string} -- Class alias

        Raises:
            Exception -- raises an exception if the alias does not exists

        Returns:
            object -- instance of the aliased class
        """
        klass = self.aliases.get(alias, None)

        if klass is None:
            msg = "Class with alias '{}' does not exist.".format(alias)
            self.log.critical(msg)
            print_failure(msg)
            sys.exit(1)

        return klass()

    def run(self):
        """Run the app."""
        self.cmd_manager.dispatch()
        self.log.info('Run App')

    def register_commands(self):
        """Register custom cli commands.

        Returns:
            dict -- commands to register
        """
        return {}

    def register_aliases(self):
        """Register aliases for classes."""
        self.log.info('Register Aliases')
        self.aliases = {
            'migrator': lambda: Migrator(self.config.get('storage.migrations.path', 'migrations'))
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
            dict -- Default commands
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
        fh = logging.FileHandler(filename, mode='a+')
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter(self.config.get(
            'app.logging.format',
            '[%(asctime)s] - [%(levelname)s] - [%(module)s] - %(message)s'
        )))
        self.log.addHandler(fh)
