"""Concrete Implementation of a data store based on SQLAlchemy.

Uses the SQLAlchemy ORM to implement the :py:mod:`.AbstractStore` interface.
"""
from experimentum.Storage import AbstractStore
from experimentum.Storage.SQLAlchemy import SQLitePlatform, Platform, ColumnFactory
from sqlalchemy import inspect, MetaData, Table


class Store(AbstractStore):

    """Concrete Implementation of a data store based on SQLAlchemy.

    Attributes:
        app (App): Framework App class.
        engine (sqlalchemy.engine.Engine): Defaults to None. Database engine.
        meta (sqlqlchemy.schema.MetaData): Defaults to None. Schema Meta Data.
        platform (Platform): Basic SQL Statements because SQLAlchemy could not handle everything.
        sqlite_platform (SQLitePlatform): SQLite specific sql statements.
    """

    def __init__(self, app):
        """Set app and load platform handlers.

        Args:
            app (App): Framework App class.
        """
        self.app = app
        self.platform = Platform()
        self.sqlite_platform = SQLitePlatform()
        self.factory = ColumnFactory()
        self.engine = None
        self.meta = None

    def set_engine(self, engine):
        """Set database engine, metadata store, and platform specific handlers.

        Args:
            engine (sqlalchemy.engine.Engine): Database engine
        """
        self.engine = engine
        self.meta = MetaData()
        self.meta.bind = self.engine
        self.meta.reflect()  # Reflecting All Tables at Once
        self.platform.set_engine(self.engine, self.meta)
        self.sqlite_platform.set_engine(self.engine, self.meta)

    def has_table(self, table):
        """Check if the data store has a specific table.

        Args:
            table (str): Name of the Table

        Returns:
            boolean
        """
        inspector = inspect(self.engine)
        return table in inspector.get_table_names()

    def has_column(self, table, column):
        """Check if a table has a specific column.

        Args:
            table (str): Name of the table
            column (str): Name of the column

        Returns:
            boolean
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table)
        for col in columns:
            if col.get('name') == column:
                return True

        return False

    def drop(self, name, checkfirst=False):
        """Drop a table from the data store.

        Notes:
            http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Args:
            name (str): Name of the table
            checkfirst (bool, optional): Defaults to False. Whether to check if exists first.
        """
        table = Table(name, self.meta)
        table.drop(self.engine, checkfirst=checkfirst)

    def drop_if_exists(self, name):
        """Drop a table from the datastore if it exists.

        Notes:
            http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Args:
            name (str): Name of the table
        """
        table = Table(name, self.meta)
        table.drop(self.engine, checkfirst=True)

    def rename(self, old, new):
        """Rename a table.

        Args:
            old (str): Old table name
            new (str): New table name
        """
        self.engine.execute(self.platform.get_rename_sql(old, new))

    def create(self, blueprint):
        """Create a new Table with Columns and indexes.

        Notes:
            http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Args:
            blueprint (Blueprint): The Blueprint to create the table
        """
        # Collection of columns and indexes
        data = self.factory.get_columns_and_indexes(blueprint)
        data['columns'].extend(data['indexes'])

        # Create table
        table = Table(blueprint.table, self.meta, *data['columns'], extend_existing=True)
        table.create(self.engine, checkfirst=True)

    def alter(self, blueprint):
        """Alter Schema of the table.

        Args:
            blueprint (Blueprint): The new blueprint with updated schema.
        """
        # Get columns and indexes
        data = self.factory.get_columns_and_indexes(blueprint)

        # Alter SQLite Database
        if self.platform.is_sqlite():
            data['columns'].extend(data['indexes'])
            self.sqlite_platform.alter_table(blueprint.table, data['columns'], blueprint.dropped)
            return

        # Alter SQL Database -> Add Columns and keys
        table = Table(blueprint.table, self.meta, extend_existing=True)
        for column in data['columns']:
            if not self.has_column(blueprint.table, column.name):
                table.append_column(column)
                self.engine.execute(self.platform.get_add_column_sql(blueprint.table, column))

            # Foreign Kyes and Primary Keys
            key_sql = self.platform.get_key_sql(blueprint.table, column)
            for sql in key_sql:
                self.engine.execute(sql)

        # Create indexes
        for index in data['indexes']:
            table.append_constraint(index)
            index.create()

        # Drop indexes
        for drop_idx in blueprint.dropped['indexes']:
            self.engine.execute(self.platform.get_drop_key_constraint_sql(
                blueprint.table,
                table.columns[drop_idx['col']],
                drop_idx['type'],
                drop_idx['name']
            ))

        # Drop Columns
        drop_sql = self.platform.get_drop_columns_sql(
            blueprint.table,
            list(set(table.columns.keys()) & set(blueprint.dropped['columns']))
        )
        for sql in drop_sql:
            self.engine.execute(sql)
