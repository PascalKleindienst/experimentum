"""Handle all migration related stuff, and provides the following classes/modules.

:py:mod:`.Schema`
    The :py:class:`.Schema` Builder lets you create, delete, or alter tables.

:py:mod:`.Blueprint` Module
    The :py:class:`.Blueprint` class lets you create, delete, or alter columns of a table.

:py:mod:`.Migration` Module
    The :py:class:`.Migration` class handles database migrations.

:py:mod:`.Migrator` Module
    The :py:class:`.Migrator` class handles the management of all migrations.

:py:mod:`.Column` Module
    Datastructure for columns.

:py:mod:`.ForeignKey` Module
    Datastructure for foreign keys.
"""
# flake8: noqa
from .Migrator import Migrator
from .Migration import Migration
from .Column import Column
from .ForeignKey import ForeignKey
from .Blueprint import Blueprint
from .Schema import Schema
