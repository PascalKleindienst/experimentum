"""Interface of the data store to make it possible to switch between different implementations."""
from __future__ import unicode_literals
from six import add_metaclass
from abc import abstractmethod, ABCMeta


@add_metaclass(ABCMeta)
class AbstractStore(object):

    """Contains the interface between the framework and the concrete Database implementation."""

    @abstractmethod
    def has_table(self, table):
        """Check if the data store has a specific table.

        Args:
            table (str): Name of the Table

        Raises:
            NotImplementedError: if method is not implemented by derived class.

        Returns:
            boolean
        """
        raise NotImplementedError('Must has_table rename method')

    def has_column(self, table, column):
        """Check if a table has a specific column.

        Args:
            table (str): Name of the table
            column (str): Name of the column

        Raises:
            NotImplementedError: if method is not implemented by derived class.

        Returns:
            boolean
        """
        raise NotImplementedError('Must has_column rename method')

    @abstractmethod
    def create(self, blueprint):
        """Create a new Table.

        Args:
            blueprint (Blueprint): The Blueprint to create the table

        Raises:
            NotImplementedError: if method is not implemented by derived class.
        """
        raise NotImplementedError('Must implement rename method')

    @abstractmethod
    def rename(self, old, new):
        """Rename a table.

        Args:
            old (str): Old table name
            new (str): New table name

        Raises:
            NotImplementedError: if method is not implemented by derived class.
        """
        raise NotImplementedError('Must implement rename method')

    @abstractmethod
    def drop(self, name, checkfirst=False):
        """Drop a table.

        Args:
            name (str): Name of the table

        Raises:
            NotImplementedError: if method is not implemented by derived class.
        """
        raise NotImplementedError('Must implement drop method')

    @abstractmethod
    def alter(self, blueprint):
        """Alter the schema for a table.

        Args:
            blueprint (Blueprint): Table Blueprint

        Raises:
            NotImplementedError: if method is not implemented by derived class.
        """
        raise NotImplementedError('Must implement alter method')
