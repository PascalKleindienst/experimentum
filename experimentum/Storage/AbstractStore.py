from abc import ABCMeta, abstractmethod


class AbstractStore(object):

    """Contains the interface between the framework and the concrete Database implementation."""
    __metaclass__ = ABCMeta

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
