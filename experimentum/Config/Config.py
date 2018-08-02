class Config(object):

    """Manages all the config items.

    Arguments:
        items {dict} -- config items
    """
    items = {}

    def has(self, key):
        """Determine if the given configuration value exists.

        Arguments:
            key {string} -- config item

        Returns:
            bool
        """
        return True if self._dot(key, False) is not False else False

    def get(self, key, default=None):
        """Get the specified configuration value.

        Arguments:
            key {string|list} -- Set of keys

        Keyword Arguments:
            default {object} -- A default value if the key is
                not found (default: {None})

        Returns:
            object -- The config value.
        """
        if isinstance(key, list):
            return self.getMany(key)

        return self._dot(key, default)

    def all(self):
        """Get all of the configuration items for the application.

        Returns:
            dict -- config items
        """
        return self.items

    def getMany(self, keys):
        """Get many configuration values.

        Arguments:
            keys {list} -- names of the keys

        Returns:
            dict -- config items for the set of keys
        """
        return {
            key: self._dot(key, default) for key, default in keys
        }

    def _dot(self, path, default):
        """Get an item using using "dot" notation.

        Arguments:
            path {string} -- Path in dot notation
            default {object} -- Default value

        Returns:
            object -- config item
        """
        arr = self.items
        keys = path.split('.')

        for key in keys:
            arr = arr.get(key, default)
            if not isinstance(arr, dict):
                return arr

        return arr

    def set(self, key, value=None):
        """Set a given configuration value.

        Arguments:
            key {list|string} -- Config item keys to change the value

        Keyword Arguments:
            value {object} -- New value (default: {None})
        """
        keys = key if isinstance(key, list) else {key: value}
        self.items.update(keys)
