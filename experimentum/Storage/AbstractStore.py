from __future__ import unicode_literals
import sys
import abc
from abc import abstractmethod

# Python2 and 3 Compatible Metaclass
if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})


class AbstractStore(ABC):

    """Contains the interface between the framework and the concrete Database implementation."""

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
