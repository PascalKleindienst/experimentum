"""SQL Platform specific code.

Generate SQL queries for altering tables and columns because
SQLAlchemy mostly does not support these types of operations.
"""
from sqlalchemy.dialects.mysql.base import MySQLDialect
from sqlalchemy.dialects.mssql.base import MSDialect
from sqlalchemy.dialects.sqlite.base import SQLiteDialect
from sqlalchemy.dialects.postgresql.base import PGDialect


class Platform(object):

    """Gettings some sql platform specific queries.

    Attributes:
        engine (sqlalchemy.engine.Engine): Database Engine
        meta (sqlalchemy.schema.MetaData): Schema Metadata
    """

    @staticmethod
    def get_rename_sql(old, new):
        """Get the sql for renaming a table.

        Args:
            old (str): old table name
            new (str): new table name

        Returns:
            str
        """
        return 'ALTER TABLE {} RENAME TO {};'.format(old, new)

    @staticmethod
    def get_drop_columns_sql(table, columns):
        """Get a list of sql commands for dropping columns.

        Args:
            table (str): name of the table
            columns (list): list of column names

        Returns:
            list
        """
        return ['ALTER TABLE {} DROP COLUMN {};'.format(table, column) for column in columns]

    @staticmethod
    def get_foreign_key_action_sql(foreign_key):
        """Get ONUPDATE/ONDELETE actions.

        Args:
            foreign_key (sqlalchemy.schema.ForeignKey): ForeignKey to get action of.

        Returns:
            dict
        """
        actions = {
            'on_delete': '',
            'on_update': ''
        }

        if foreign_key.ondelete:
            actions['on_delete'] = 'ON DELETE {}'.format(foreign_key.ondelete)
        if foreign_key.onupdate:
            actions['on_update'] = 'ON UPDATE {}'.format(foreign_key.onupdate)

        return actions

    def __init__(self):
        """Initialize platform."""
        self.engine = None
        self.meta = None

    def set_engine(self, engine, meta):
        """Set engine and meta.

        Args:
            engine (sqlalchemy.engine.Engine): Database Engine
            meta (sqlalchemy.schema.MetaData): Schema Metadata
        """
        self.engine = engine
        self.meta = meta

    def is_sqlite(self):
        """Check if current database driver is SQLite.

        Returns:
            boolean
        """
        return isinstance(self.engine.dialect, SQLiteDialect)

    def is_mysql(self):
        """Check if current database driver is MySQL.

        Returns:
            boolean
        """
        return isinstance(self.engine.dialect, MySQLDialect)

    def is_mssql(self):
        """Check if current database driver is MSSQL.

        Returns:
            boolean
        """
        return isinstance(self.engine.dialect, MSDialect)

    def is_postgresql(self):
        """Check if current database driver is PostgreSQL.

        Returns:
            boolean
        """
        return isinstance(self.engine.dialect, PGDialect)

    def get_add_column_sql(self, table, column):
        """Get SQL for adding a column to a table.

        Notes:
            - https://stackoverflow.com/questions/7300948/add-column-to-sqlalchemy-table#17243132
            - http://docs.sqlalchemy.org/en/latest/core/compiler.html

        Args:
            table (str): Name of the table
            column (sqlalchemy.schema.Column): Column to add

        Returns:
            str
        """
        column_name = column.compile(dialect=self.engine.dialect)
        column_type = column.type.compile(self.engine.dialect)

        # postgresql does not like the table.column syntax
        if self.is_postgresql():
            column_name = column.name

        return 'ALTER TABLE {table} ADD COLUMN {column} {type};'.format(
            table=table,
            column=column_name,
            type=column_type
        )

    def get_key_sql(self, table, column):
        """Get SQL for adding foreign key and primary key constraints.

        Args:
            table (str): Name of the table
            column (sqlalchemy.schema.Column): Column to add contraints on

        Returns:
            list: List of strings with SQL commands
        """
        sql = []

        # add foreign keys
        for fkey in column.foreign_keys:
            actions = self.get_foreign_key_action_sql(fkey)
            sql.append(
                'ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {}({}) {} {};'.format(
                    table,
                    fkey.name.replace('.', '__'),
                    column.name,
                    fkey.target_fullname.split('.')[0],
                    fkey.target_fullname.split('.')[1],
                    actions['on_delete'],
                    actions['on_update']
                )
            )

        # add primary key if needed
        if column.primary_key:
            sql.append('ALTER TABLE {} ADD PRIMARY KEY({});'.format(
                table,
                column.compile(dialect=self.engine.dialect)
            ))

        return sql

    def get_drop_key_constraint_sql(self, table, column, idx_type, idx_name):
        """Get a drop key constraint sql query.

        Args:
            table (str): Name of table
            column (sqlalchemy.schema.Column): Column with the key
            idx_type (str): Type of index, i.e. primary, foreign, unique or index
            idx_name (str): Name of the index

        Returns:
            str
        """
        column_name = column.compile(dialect=self.engine.dialect)
        column_type = column.type.compile(self.engine.dialect)

        if idx_type == 'primary':
            if self.is_mysql():
                return 'ALTER TABLE {0} CHANGE {1} {1} {2} UNSIGNED NOT NULL; ' \
                    'ALTER TABLE {0} DROP PRIMARY KEY;'.format(table, column_name, column_type)

            return 'ALTER TABLE {} DROP CONSTRAINT {};'.format(table, idx_name)
        elif idx_type == 'unique':
            return 'ALTER TABLE {} DROP {} {};'.format(
                table,
                'INDEX' if self.is_mysql() else 'CONSTRAINT',
                idx_name
            )
        elif idx_type == 'foreign':
            return 'ALTER TABLE {} DROP {} {};'.format(
                table,
                'FOREIGN KEY' if self.is_mysql() else 'CONSTRAINT',
                idx_name
            )
        elif idx_type == 'index':
            if self.is_mssql():
                return 'DROP INDEX {} ON {};'.format(idx_name, table)
            elif self.is_mysql():
                return 'ALTER TABLE {} DROP INDEX {};'.format(table, idx_name)

            return 'DROP INDEX {};'.format(idx_name)
