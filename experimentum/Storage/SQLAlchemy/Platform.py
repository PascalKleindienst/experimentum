class Platform(object):

    """Gettings some sql platform specific queries.

    Attributes:
        engine {Engine} -- Database Engine
        meta {MetaData} -- Schema Metadata
    """

    def __init__(self):
        """Initialize platform."""
        self.engine = None
        self.meta = None

    def set_engine(self, engine, meta):
        """Set engine and meta.

        Arguments:
            engine {Engine} -- Database Engine
            meta {MetaData} -- Schema Metadata
        """
        self.engine = engine
        self.meta = meta

    def get_add_column_sql(self, table, column):
        """Get SQL for adding a column to a table.

        See:
        * https://stackoverflow.com/questions/7300948/add-column-to-sqlalchemy-table#17243132
        * http://docs.sqlalchemy.org/en/latest/core/compiler.html#dialect-specific-compilation-rules

        Arguments:
            table {string} -- Name of the table
            column {Column} -- Column to add

        Returns:
            string
        """
        column_name = column.compile(dialect=self.engine.dialect)
        column_type = column.type.compile(self.engine.dialect)

        return 'ALTER TABLE {table} ADD COLUMN {column} {type};'.format(
            table=table,
            column=column_name,
            type=column_type
        )

    def get_key_sql(self, table, column):
        """Get SQL for adding foreign key and primary key constraints.

        Arguments:
            table {string} -- Name of the table
            column {Column} -- Column to add contraints on

        Returns:
            list -- List of strings with SQL commands
        """
        sql = []

        # add foreign keys
        for fkey in column.foreign_keys:
            actions = self._get_foreign_key_action_sql(fkey)
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

    def get_rename_sql(self, old, new):
        """Get the sql for renaming a table.

        Arguments:
            old {string} -- old table name
            new {string} -- new table name

        Returns:
            string
        """
        return 'ALTER TABLE {} RENAME TO {};'.format(old, new)

    def get_drop_columns_sql(self, table, columns):
        """Get a list of sql commands for dropping columns.

        Arguments:
            table {string} -- name of the table
            columns {list} -- list of column names

        Returns:
            list
        """
        return ['ALTER TABLE {} DROP COLUMN {};'.format(table, column) for column in columns]

    def _get_foreign_key_action_sql(self, foreign_key):
        """Get ONUPDATE/ONDELETE actions.

        Arguments:
            foreign_key {ForeignKey} -- ForeignKey to get action of.

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
