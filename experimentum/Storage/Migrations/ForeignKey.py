r"""ForeignKey data structure to configure foreign key attributes.

Supports method chaining to easily configure foreign keys, like::

    table.foreign('user_id').references('id').on('users')\
        .on_delete('cascade')\
        .on_update('cascade')
"""


class ForeignKey(object):

    """Stores attributes for a Foreign Key."""

    def __init__(self, column, name=None):
        """Set Attributes.

        Args:
            column (str): Column of the foreign key
            name (str, optional): Defaults to None. Name of the foreign key.
        """
        self._attributes = {
            'column': column,
            'name': name,
            'ref_table': None,
            'ref_column': None,
            'on_delete': None,
            'on_update': None
        }

    def references(self, ref_column):
        """Set the column the foreign key references.

        Args:
            ref_column (str): Name of referenced column

        Returns:
            ForeignKey: self instance for method chaining.
        """
        self._attributes['ref_column'] = ref_column
        return self

    def on(self, ref_table):
        """Set the table the foreign key references.

        Args:
            ref_table (str): Name of the referenced table

        Returns:
            ForeignKey: self instance for method chaining.
        """
        self._attributes['ref_table'] = ref_table
        return self

    def on_delete(self, action):
        """Set the action which will be executed on delete.

        Args:
            action (str): Action to execute

        Returns:
            ForeignKey: self instance for method chaining.
        """
        self._attributes['on_delete'] = action
        return self

    def on_update(self, action):
        """Set the action which will be executed on update.

        Args:
            action (str): Action to execute

        Returns:
            ForeignKey: self instance for method chaining.
        """
        self._attributes['on_update'] = action
        return self

    def get(self, attribute, default=None):
        """Get the value of an attribute, with a default if it does not exist.

        Args:
            attribute (str): Attribute you want to get
            default (object, optional): Defaults to None. Default value.

        Returns:
            object
        """
        return self._attributes.get(attribute, default)
