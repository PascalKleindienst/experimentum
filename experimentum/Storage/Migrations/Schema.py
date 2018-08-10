import sys
from experimentum.Commands import print_failure
from contextlib import contextmanager


class Schema(object):

    """Inspired by the Laravel Schema Builder (https://laravel.com/docs/5.6/migrations#tables).

    Attributes:
        app {App} -- Main App Class
        store {AbstractStore} -- Data Store
    """

    def __init__(self, app):
        """Set app and store.

        Arguments:
            app {App} -- Main App Class
        """
        self.app = app
        self.store = app.make('store')

    @contextmanager
    def create(self, name):
        """Create a new table blueprint.

        Arguments:
            name {string} -- Name of the table

        Returns:
            Blueprint
        """
        try:
            blueprint = self.app.make('blueprint', name)
            blueprint.create()

            yield blueprint
        except Exception as e:
            print_failure('Error while creating blueprint')
            self.app.log.critical('Error while creating blueprint: ' + str(e))
            sys.exit(1)

        self._build(blueprint)

    @contextmanager
    def table(self, name):
        """Create a blueprint for an existing table.

        Arguments:
            name {string} -- Name of the table

        Returns:
            Blueprint
        """
        try:
            blueprint = self.app.make('blueprint', name)

            yield blueprint
        except Exception as e:
            print_failure('Error while creating blueprint')
            self.app.log.critical('Error while creating blueprint: ' + str(e))
            sys.exit(1)

        self._build(blueprint)

    def rename(self, old, new):
        """Rename a table.

        Arguments:
            old {string} -- Old table name
            new {string} -- New table name
        """
        self.store.rename(old, new)

    def drop(self, name):
        """Drop a table.

        Arguments:
            name {string} -- Name of the table
        """
        self.store.drop(name)

    def drop_if_exists(self, name):
        """Drop a table if it exists.

        Arguments:
            name {string} -- Name of the table
        """
        self.store.drop_if_exists(name)

    def has_table(self, table):
        """Check if database has a specific table.

        Arguments:
            table {string} -- Table to check existance of
        """
        return self.store.has_table(table)

    def has_column(self, table, column):
        """Check if table has a specific column.

        Arguments:
            table {string} -- Table to check
            column {string} -- Column to check
        """
        return self.store.has_column(table, column)

    def _build(self, blueprint):
        """Build Schema based on the blueprint.

        Arguments:
            blueprint {Blueprint} -- Blueprint to build
        """
        if blueprint.action is 'create':
            self.store.create(blueprint)
        elif blueprint.action is 'alter':
            self.store.alter(blueprint)
