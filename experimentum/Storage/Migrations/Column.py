class Column(object):

    """Stores attributes the the column."""

    def __init__(self, type, name, parameters):
        """Set Attributes.

        Arguments:
            type {string} -- Type of the column
            name {string} -- Name of the column
            parameters {object} -- Additional parameters for the column
        """
        self._attributes = {
            'type': type,
            'name': name,
            'parameters': parameters,
            'null': False,
            'default': None,
            'unsigned': False,
        }

    def get(self, attribute, default=None):
        """Get the value of an attribute, with a default if it does not exist.

        Arguments:
            attribute {string} -- Attribute you want to get

        Keyword Arguments:
            default {object} -- Default value (default: {None})

        Returns:
            object
        """
        return self._attributes.get(attribute, default)

    def nullable(self):
        """Designate that the column allows NULL values.

        Returns:
            Column
        """
        self._attributes['null'] = True
        return self

    def default(self, value):
        """Specify a default value for the column.

        Arguments:
            value {object} -- The default value

        Returns:
            Column
        """
        self._attributes['default'] = value
        return self

    def unsigned(self):
        """Set INTEGER column as UNSINGED (MySQL).

        Returns:
            Column
        """
        self._attributes['unsigned'] = True
        return self

    def __repr__(self):
        """Human-readable representation of the column attributes.

        Returns:
            string
        """
        return '{}'.format(self._attributes)
