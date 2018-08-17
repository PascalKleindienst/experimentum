from __future__ import unicode_literals
from six import add_metaclass
from abc import abstractmethod, ABCMeta


@add_metaclass(ABCMeta)
class AbstractStore(object):

    """Contains the interface between the framework and the concrete Database implementation."""

    @abstractmethod
    def has_table(self, table):
        """Check if the data store has a specific table.

        Arguments:
            table {string} -- Name of the Table

        Returns:
            boolean
        """
        raise NotImplementedError('Must has_table rename method')

    def has_column(self, table, column):
        """Check if a table has a specific column.

        Arguments:
            table {string} -- Name of the table
            column {string} -- Name of the column

        Returns:
            boolean
        """
        raise NotImplementedError('Must has_column rename method')

    @abstractmethod
    def create(self, blueprint):
        """Create a new Table.

        Arguments:
            blueprint {Blueprint} -- The Blueprint to create the table
        """
        raise NotImplementedError('Must implement rename method')

    @abstractmethod
    def rename(self, old, new):
        """Rename a table.

        Arguments:
            old {string} -- Old table name
            new {string} -- New table name
        """
        raise NotImplementedError('Must implement rename method')

    @abstractmethod
    def drop(self, name, checkfirst=False):
        """Drop a table.

        Arguments:
            name {string} -- Name of the table
        """
        raise NotImplementedError('Must implement drop method')

    @abstractmethod
    def alter(self, blueprint):
        """Alter the schema for a table.

        Arguments:
            blueprint {Blueprint} -- Table Blueprint
        """
        raise NotImplementedError('Must implement alter method')
