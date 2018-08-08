class ForeignKey(object):

    """Stores attributes for a Foreign Key."""

    def __init__(self, column, name=None):
        """Set Attributes.

        Arguments:
            column {string} -- Column of the foreign key

        Keyword Arguments:
            name {string} -- Name of the foreign key (default: {None})
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

        Arguments:
            ref_column {string} -- Name of referenced column

        Returns:
            ForeignKey
        """
        self._attributes['ref_column'] = ref_column
        return self

    def on(self, ref_table):
        """Set the table the foreign key references.

        Arguments:
            ref_table {string} -- Name of the referenced table

        Returns:
            ForeignKey
        """
        self._attributes['ref_table'] = ref_table
        return self

    def on_delete(self, action):
        """Set the action which will be executed on delete.

        Arguments:
            action {string} -- Action to execute

        Returns:
            ForeignKey
        """
        self._attributes['on_delete'] = action
        return self

    def on_update(self, action):
        """Set the action which will be executed on update.

        Arguments:
            action {string} -- Action to execute

        Returns:
            ForeignKey
        """
        self._attributes['on_update'] = action
        return self

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
