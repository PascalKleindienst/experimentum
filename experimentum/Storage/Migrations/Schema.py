"""The :py:class:`.Schema` class provides a database agnostic way of manipulating tables.

Tables
======

Creating Tables
---------------
To create a new database table, the :py:meth:`~.Schema.create` method is used.
The :py:meth:`~.Schema.create` method accepts a table name as its argument and returns
a :py:class:`.Blueprint` instance that can be used to define the new table.
When creating the table, you may use any of the :py:class:`.Blueprint` column methods
to define the table's columns::

    with self.schema.create('users') as table:
        table.increments('id')

Checking Existence
------------------
To check if a table or column exist you can use the :py:meth:`~.Schema.has_table` or
:py:meth:`~.Schema.has_column` methods respectively::

    if self.schema.has_table('users'):
        # ...

    if self.schema.has_column('users', 'email'):
        # ...

Renaming / Dropping Tables
--------------------------
To rename an existing database table, use the :py:meth:`~.Schema.rename` method::

    self.schema.rename('from', 'to')

To drop a table, you can use the :py:meth:`~.Schema.drop` or
:py:meth:`~.Schema.drop_if_exists` methods::

    self.schema.drop('users')
    self.schema.drop_if_exists('users')
"""
from experimentum.cli import print_failure
from contextlib import contextmanager


class Schema(object):

    """Database agnostic way of manipulating tables.

    The :py:class:`.Schema` class was inspired by the Laravel Schema Builder
    (https://laravel.com/docs/5.6/migrations#tables).

    Attributes:
        app (App): Main App Class.
        store (AbstractStore): Data Store.
    """

    def __init__(self, app):
        """Set app and store.

        Args:
            app (App): Main App Class.
        """
        self.app = app
        self.store = app.make('store')

    @contextmanager
    def create(self, name):
        """Create a new table blueprint.

        Args:
            name (str): Name of the table.

        Yields:
            Blueprint: New Instance of a table blueprint
        """
        try:
            blueprint = self.app.make('blueprint', name)
            blueprint.create()

            yield blueprint
        except Exception as exc:
            print_failure('Error while creating blueprint: ' + str(exc), 1)

        self._build(blueprint)

    @contextmanager
    def table(self, name):
        """Create a blueprint for an existing table.

        Args:
            name (str): Name of the table

        Yields:
            Blueprint: New Instance of a table blueprint
        """
        try:
            blueprint = self.app.make('blueprint', name)

            yield blueprint
        except Exception as exc:
            print_failure('Error while creating blueprint: ' + str(exc), 1)

        self._build(blueprint)

    def rename(self, old, new):
        """Rename a table.

        Args:
            old (str): Old table name
            new (str): New table name
        """
        self.store.rename(old, new)

    def drop(self, name):
        """Drop a table.

        Args:
            name (str): Name of the table
        """
        self.store.drop(name)

    def drop_if_exists(self, name):
        """Drop a table if it exists.

        Args:
            name (str): Name of the table
        """
        self.store.drop_if_exists(name)

    def has_table(self, table):
        """Check if database has a specific table.

        Args:
            table (str): Table to check existance of
        """
        return self.store.has_table(table)

    def has_column(self, table, column):
        """Check if table has a specific column.

        Args:
            table (str): Table to check
            column (str): Column to check
        """
        return self.store.has_column(table, column)

    def _build(self, blueprint):
        """Build Schema based on the blueprint.

        Args:
            blueprint (Blueprint): Blueprint to build.
        """
        if blueprint.action == 'create':
            self.store.create(blueprint)
        elif blueprint.action == 'alter':
            self.store.alter(blueprint)
