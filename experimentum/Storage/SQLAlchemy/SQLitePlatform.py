from experimentum.Storage.SQLAlchemy import Platform
from sqlalchemy.dialects.sqlite import pysqlcipher, pysqlite
from sqlalchemy import Table, Index, ForeignKey


class SQLitePlatform(Platform):

    """SQLite specific sql commands and queries."""

    def is_sqlite_dialect(self):
        """Check if dialect is a sqlite dialect.

        Returns:
            boolean
        """
        return (
            isinstance(self.engine.dialect, pysqlcipher.SQLiteDialect_pysqlcipher) or
            isinstance(self.engine.dialect, pysqlite.SQLiteDialect_pysqlite)
        )

    def alter_table(self, table, cols, dropped):
        """Alter SQLite Table.

        SQLite does not provide complete ALTER TABLE support, only RENAME TABLE and ADD COLUMN
        variants are supported. In order to add columns and keys we have to create a tempory
        table which holds the data of the table and then drop and recreate the table with
        the modified schema. Lastly we have to copy the data back into the new table and
        delete the temporary data table.

        See:
        https://www.sqlite.org/omitted.html

        Arguments:
            table {string} -- Name of the table
            cols {list} -- List with changed columns
            dropped {list} -- List with columns to drop
        """
        # Prepare columns
        old_table = self.meta.tables.get(table, Table(table, self.meta, autoload=True))
        columns = self._prepare_columns(list(old_table.columns), dropped)
        new_columns = columns['columns']
        new_columns.extend(cols)

        # * CREATE TABLE $data_table AS SELECT ($old_cols) FROM $old_table;
        data_table = self._create_table('__tmp__{}'.format(table), columns['columns'])

        # * DROP TABLE $old_table;
        old_table.drop(self.engine)

        # * CREATE TABLE $new_table ($old_columns + $new_columns);
        self._create_table('__new__{}__'.format(table), new_columns)
        self.engine.execute(self.get_rename_sql('__new__{}__'.format(table), table))

        # * INSERT INTO $new_table ($old_column) SELECT * FROM $data_table;
        self._fill_table(table, columns['names'], data_table)

        # * DROP TABLE $data_table;
        data_table.drop(self.engine)

    def _prepare_columns(self, columns, dropped):
        """Prepate columns so that they can be created for another table.

        Arguments:
            columns {list} -- Columns of a table
            dropped {list} -- Columns to drop

        Returns:
            dict
        """
        data = {'columns': [], 'names': []}

        for col in columns:
            column = col.copy()

            # Add Foreign Keys
            fkeys = []
            for fkey in col.foreign_keys:
                fkeys.append(ForeignKey(
                    fkey.column,
                    name=fkey.name,
                    onupdate=fkey.onupdate,
                    ondelete=fkey.ondelete,
                    deferrable=fkey.deferrable
                ))
            column.foreign_keys = set(fkeys)

            # Add column and names
            if column.name not in dropped:
                data['columns'].append(column)
                data['names'].append(column.name)

        return data

    def _fill_table(self, target_tablename, columns, source_table):
        """Fill a target table with values from a source table.

        Arguments:
            target_tablename {string} -- Table to be filled
            columns {list} -- List of columns to be filled
            source_table {string} -- Name of the source table
        """
        self.engine.execute('INSERT INTO {} ({}) SELECT {} FROM {}'.format(
            target_tablename,
            ','.join(columns),
            ','.join(columns),
            source_table
        ))

    def _create_table(self, tablename, columns):
        """Create a new table with columns and constraints.

        Arguments:
            tablename {string} -- Name of new table
            columns {list} -- List of Columns

        Returns:
            Table
        """
        table = Table(tablename, self.meta, extend_existing=True)
        for column in columns:
            if isinstance(column, Index):
                table.append_constraint(column)
            else:
                table.append_column(column.copy())
        table.create(self.engine, checkfirst=True)

        return table
