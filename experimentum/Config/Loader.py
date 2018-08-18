"""The Config Loader module loads json config files.

The :py:mod:`.Loader` loads all json files from a folder
and stores the content in the :py:mod:`.Config` module.
"""

import logging
import json
import glob
import os
import io


class Loader(object):

    """Load the configuration files.

    Attributes:
        config_path (string): Path to config files.
        config (Config): Config holder class
    """

    def __init__(self, config_path, config):
        """Load the configuration items.

        Arguments:
            config_path (string): Path to config files.
            config (Config): Config holder class.
        """
        self.config_path = config_path
        self.config = config

    def load_config_files(self):
        """Load the configuration items from all of the files.

        Raises:
            Exception: if there is no app.json config.
        """
        files = self.get_config_files()

        if 'app' not in files:
            logging.critical('Unable to load the "app" configuration file.')
            raise Exception('Unable to load the "app" configuration file.')

        for key, path in files.items():
            with io.open(path, encoding='utf-8') as fh:
                self.config.set(key, json.load(fh))

    def get_config_files(self):
        """Get all of the configuration files for the application.

        Returns:
            dict: The config items.
        """
        files = glob.glob(os.path.join(self.config_path, '*.json'))

        return {
           self._config_key(file): os.path.realpath(file) for file in files
        }

    def _config_key(self, fname):
        """Get the config key based on the filename.

        Arguments:
            fname (string): Name of the config file.

        Returns:
            string: key
        """
        return os.path.splitext(os.path.basename(fname))[0]
