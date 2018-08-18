"""The config module stores all config items.

The Config class supports the *dot-notation* which means that you
can access nested elements seperated by a ``.``, e.g. ``foo.bar.baz``.

Example:

.. code-block:: python

    cfg = Config()
    cfg.set({ 'foo': 'bar', 'foobar': {'baz': 42 } })

    cfg.get('foobar.baz')  # returns: 42
    cfg.has('foobar.foo')  # returns: False
    cfg.all()              # returns: { 'foo': 'bar', 'foobar': {'baz': 42 } }

"""


class Config(object):

    """Manages all the config items.

    Attributes:
        items (dict): Loaded config items.
    """

    def __init__(self):
        """Init config store."""
        self.items = {}

    def has(self, key):
        """Determine if the given configuration value exists.

        Args:
            key (string): config item key

        Returns:
            bool
        """
        return True if self._dot(key, False) is not False else False

    def get(self, key, default=None):
        """Get the specified configuration value.

        Args:
            key (string|list): Set of keys.
            default (object, optional): Defaults to None. A default value if the key is
                not found

        Returns:
            object: The config value.
        """
        if isinstance(key, list):
            return self.getMany(key)

        return self._dot(key, default)

    def all(self):
        """Get all of the configuration items for the application.

        Returns:
            dict: config items
        """
        return self.items

    def getMany(self, keys):
        """Get many configuration values.

        Arguments:
            keys (list): Names of the keys.

        Returns:
            dict: Donfig items for the set of keys.
        """
        return {
            key: self._dot(key, default) for key, default in keys
        }

    def _dot(self, path, default):
        """Get an item using using "dot" notation.

        Arguments:
            path (string): Path in dot notation
            default (object): Default value

        Returns:
            object: config item
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
            key (dict|string): Config item keys to change the value
            value (object,optional): Defaults to None. New value
        """
        keys = key if isinstance(key, dict) else {key: value}
        self.items.update(keys)
