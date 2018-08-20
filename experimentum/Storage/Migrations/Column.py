"""Column Data Structure to add column modifiers.

Add column modifiers like nullable, default, unsigned to
a column. They support method chaining, so the following is possible::

    table.integer('foo').unsigned().nullable()
"""


class Column(object):

    """Stores attributes the the column."""

    def __init__(self, col_typ, name, parameters):
        """Set Attributes.

        Args:
            col_typ (str): Type of the column.
            name (str): Name of the column.
            parameters (object): Additional parameters for the column.
        """
        self._attributes = {
            'type': col_typ,
            'name': name,
            'parameters': parameters,
            'null': False,
            'default': None,
            'unsigned': False,
        }

    def get(self, attribute, default=None):
        """Get the value of an attribute, with a default if it does not exist.

        Args:
            attribute (str): Attribute you want to get.
            default (object, optional): Defaults to None. Default value if attribute is not found.

        Returns:
            object
        """
        return self._attributes.get(attribute, default)

    def nullable(self):
        """Designate that the column allows NULL values.

        Returns:
            Column: self instance for method chaining.
        """
        self._attributes['null'] = True
        return self

    def default(self, value):
        """Specify a default value for the column.

        Args:
            value (object): The default value

        Returns:
            Column: self instance for method chaining.
        """
        self._attributes['default'] = value
        return self

    def unsigned(self):
        """Set INTEGER column as UNSINGED (MySQL).

        Returns:
            Column: self instance for method chaining.
        """
        self._attributes['unsigned'] = True
        return self

    def __repr__(self):
        """Human-readable representation of the column attributes.

        Returns:
            str
        """
        return '{}'.format(self._attributes)
