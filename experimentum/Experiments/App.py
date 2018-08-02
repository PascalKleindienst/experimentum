from __future__ import print_function
import os
import logging
import logging.handlers
from experimentum.Config import Config, Loader

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
        Loader(os.path.realpath(self.config_path), self.config)

        # Setup logger
        self._set_logger()
        self.log.info('Bootstrap App')

        # save app instance
        app(self)

    def register_commands(self):
        """Register custom cli commands.

        Returns:
            dict -- commands to register
        """
        return {}

    def run(self):
        """Run the app."""
        print('Running App...')

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
