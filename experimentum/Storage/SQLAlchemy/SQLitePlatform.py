from experimentum.Storage.SQLAlchemy import Platform
from sqlalchemy import Table, Index, ForeignKey


class SQLitePlatform(Platform):

    """SQLite specific sql commands and queries."""

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
            dropped {object} -- Object with list of columns and indexes to drop
        """
        # Prepare columns
        old_table = self.meta.tables.get(table, Table(table, self.meta, autoload=True))
        columns = self._prepare_columns(list(old_table.columns), list(old_table.indexes), dropped)
        new_columns = columns['columns']
        new_columns.extend(cols)

        # * CREATE TABLE $data_table AS SELECT ($old_cols) FROM $old_table;
        data_table = self._create_table('__tmp__{}'.format(table), columns['columns'])
        self._fill_table(data_table, columns['names'], old_table)

        # * DROP TABLE $old_table;
        old_table.drop(self.engine)

        # * CREATE TABLE $new_table ($old_columns + $new_columns);
        self._create_table('__new__{}__'.format(table), new_columns)
        self.engine.execute(self.get_rename_sql('__new__{}__'.format(table), table))

        # * INSERT INTO $new_table ($old_column) SELECT * FROM $data_table;
        self._fill_table(table, columns['names'], data_table)

        # * DROP TABLE $data_table;
        data_table.drop(self.engine)

    def _prepare_columns(self, columns, indexes, dropped):
        """Prepate columns so that they can be created for another table.

        Arguments:
            columns {list} -- Columns of a table
            indexes {list} -- indexes of a table
            dropped {object} -- Columns and indexes to drop

        Returns:
            dict
        """
        data = {'columns': [], 'names': []}
        dropped_fkeys = [fkey['name'] for fkey in dropped['indexes'] if fkey['type'] == 'foreign']
        dropped_pkeys = [pkey['col'] for pkey in dropped['indexes'] if pkey['type'] == 'primary']

        # Add Columns
        for col in columns:
            column = col.copy()

            # Add Foreign Keys
            fkeys = []
            for fkey in col.foreign_keys:
                if fkey.name not in dropped_fkeys:
                    fkeys.append(ForeignKey(
                        fkey.column,
                        name=fkey.name,
                        onupdate=fkey.onupdate,
                        ondelete=fkey.ondelete,
                        deferrable=fkey.deferrable
                    ))
            column.foreign_keys = set(fkeys)

            # Drop primary keys
            if column.primary_key and column.name in dropped_pkeys:
                column.primary_key = False

            # Add column and names
            if column.name not in dropped['columns']:
                data['columns'].append(column)
                data['names'].append(column.name)

        # Add Indexes
        for idx in indexes:
            drop = False
            for drop_idx in dropped['indexes']:
                if drop_idx['name'] == idx.name:
                    drop = True
                    break

            if drop is False:
                data['columns'].append(idx)

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
        used_idx = []

        for column in columns:
            if isinstance(column, Index):
                # copy columns to avoid association with new table errors
                idx_cols = [idx_col.copy() for idx_col in column.columns]

                # Add index
                if column.name not in used_idx:
                    table.append_constraint(Index(column.name, *idx_cols, unique=column.unique))
                    used_idx.append(column.name)

                # Drop old index if exists to avoid naming conflicts
                try:
                    column.drop(self.engine)
                except Exception, e:
                    pass
            else:
                table.append_column(column.copy())

        table.create(self.engine, checkfirst=True)
        return table
