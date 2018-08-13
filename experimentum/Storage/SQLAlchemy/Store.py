from experimentum.Storage import AbstractStore
from experimentum.Storage.SQLAlchemy import SQLitePlatform, Platform
from sqlalchemy import inspect
from sqlalchemy import MetaData, Column, Table, Index, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, DOUBLE, LONGTEXT, MEDIUMINT, MEDIUMTEXT
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Date, DateTime, Enum,\
    LargeBinary, Numeric, SmallInteger, String, Text, Time, CHAR, Float, JSON, TIMESTAMP


class Store(AbstractStore):

    """Concrete Implementation of a data store based on SQLAlchemy.

    Attributes:
        app {App} -- Framework App Class
        engine {Engine} -- Database Engine
        meta {MetaData} -- Schema Meta Data
        platform {Platform} -- Basic SQL Statements because SQLAlchemy could not handle everything
        sqlite_platform {SQLitePlatform} -- SQLite specific sql statements
    """

    def __init__(self, app):
        """Set app and load platform handlers.

        Arguments:
            app {App} -- Framework App Class
        """
        self.app = app
        self.platform = Platform()
        self.sqlite_platform = SQLitePlatform()

    def set_engine(self, engine):
        """Set database engine, metadata store, and platform specific handlers.

        Arguments:
            engine {Engine} -- Database Engine
        """
        self.engine = engine
        self.meta = MetaData()
        self.meta.bind = self.engine
        self.meta.reflect()  # Reflecting All Tables at Once
        self.platform.set_engine(self.engine, self.meta)
        self.sqlite_platform.set_engine(self.engine, self.meta)

    def has_table(self, table):
        """Check if the data store has a specific table.

        Arguments:
            table {string} -- Name of the Table

        Returns:
            boolean
        """
        inspector = inspect(self.engine)
        return table in inspector.get_table_names()

    def has_column(self, table, column):
        """Check if a table has a specific column.

        Arguments:
            table {string} -- Name of the table
            column {string} -- Name of the column

        Returns:
            boolean
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table)
        for col in columns:
            if col.get('name') == column:
                return True

        return False

    def drop(self, name):
        """Drop a table from the data store.

        See:
        http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Arguments:
            name {string} -- Name of the table
        """
        table = Table(name, self.meta)
        table.drop(self.engine, checkfirst=False)

    def drop_if_exists(self, name):
        """Drop a table from the datastore if it exists.

        See:
        http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Arguments:
            name {string} -- Name of the table
        """
        table = Table(name, self.meta)
        table.drop(self.engine, checkfirst=True)

    def rename(self, old, new):
        """Rename a table.

        Arguments:
            old {string} -- Old table name
            new {string} -- New table name
        """
        self.engine.execute(self.platform.get_rename_sql(old, new))

    def create(self, blueprint):
        """Create a new Table with Columns and indexes.

        See:
        http://docs.sqlalchemy.org/en/latest/core/metadata.html#creating-and-dropping-database-tables

        Arguments:
            blueprint {Blueprint} -- The Blueprint to create the table
        """
        # Collection of columns and indexes
        data = self._get_columns_and_indexes(blueprint.columns, blueprint.indexes, blueprint.fkeys)
        data['columns'].extend(data['indexes'])

        # Create table
        table = Table(blueprint.table, self.meta, *data['columns'], extend_existing=True)
        table.create(self.engine, checkfirst=True)

    def alter(self, blueprint):
        """Alter Schema of the table.

        Arguments:
            blueprint {Blueprint} -- The new blueprint with updated schema
        """
        # Get columns and indexes
        data = self._get_columns_and_indexes(blueprint.columns, blueprint.indexes, blueprint.fkeys)

        # Alter SQLite Database
        if self.sqlite_platform.is_sqlite_dialect():
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

        # Drop Columns
        drop_sql = self.platform.get_drop_columns_sql(
            blueprint.table,
            list(set(table.columns.keys()) & set(blueprint.dropped))
        )
        for sql in drop_sql:
            self.engine.execute(sql)

    def _get_columns_and_indexes(self, columns, indexes, foreign_keys):
        """Get Column and Index instances from the blueprint.

        Arguments:
            columns {list} -- List of columns
            indexes {list} -- List of indexes
            foreign_keys {list} -- List of foreign keys

        Returns:
            dict
        """
        # Collection of columns and indexes
        data = {
            'columns': [],
            'indexes': [],
        }
        used_indexes = []

        for col in columns:
            # Get Indexes and Primary Keys
            primary, _idxs, _used_idxs = self._get_indexes(col, indexes, used_indexes)
            data['indexes'].extend(_idxs)
            used_indexes.extend(_used_idxs)

            # Add Foreign Key column
            foreign_key = self._get_foreign_key(col, foreign_keys)
            if foreign_key is not False:
                data['columns'].append(foreign_key)
                continue

            # Add Column
            data['columns'].append(Column(
                col.get('name'),
                self._get_type(
                    col.get('type'),
                    col.get('parameters'),
                    unsigned=col.get('unsigned')
                ),
                default=col.get('default'),
                nullable=col.get('null'),
                primary_key=primary
            ))

        return data

    def _create_foreign_key(self, key, col):
        """Create a foreign key column.

        Arguments:
            key {ForeignKey} -- Foreign Key
            col {Column} -- [description]

        Returns:
            Column
        """
        fkey = ForeignKey(
            key.get('ref_table') + '.' + key.get('ref_column'),
            ondelete=key.get('on_delete'),
            onupdate=key.get('on_update'),
            name=key.get('name')
        )

        return Column(
            col.get('name'),
            self._get_type(
                col.get('type'),
                col.get('parameters'),
                unsigned=col.get('unsigned')
            ),
            fkey,
            default=col.get('default'),
            nullable=col.get('null'),
        )

    def _get_foreign_key(self, col, fkeys):
        """Get a foreign key from a column.

        Arguments:
            col {Column} -- Column
            fkeys {list} -- List of foreign keys

        Returns:
            ForeignKey|False
        """
        col_name = col.get('name')
        foreign_key = [
            self._create_foreign_key(fkey.get('key'), col)
            for fkey in fkeys
            if (fkey.get('col') == col_name or col_name in fkey.get('col'))
        ]

        if len(foreign_key):
            return foreign_key[0]

        return False

    def _get_indexes(self, col, indexes, used_indexes=[]):
        """Get all indexes and primary keys of a column.

        Arguments:
            col {Column} -- The Column
            indexes {list} -- Indexes

        Keyword Arguments:
            used_indexes {list} -- Already used indexed (for composite keys) (default: {[]})

        Returns:
            dict
        """
        _indexes = []
        primary_key = False
        for idx in indexes:
            if idx.get('col') == col.get('name') or col.get('name') in idx.get('col'):
                # Primary Key
                if idx.get('type') == 'primary':
                    primary_key = True
                # Unique Index
                elif idx.get('type') == 'unique' and idx.get('col') not in used_indexes:
                    _indexes.append(
                        Index(idx.get('name'), idx.get('col'), unique=True)
                    )
                    used_indexes.append(idx.get('col'))
                # Basic Index
                elif idx.get('type') == 'index' and idx.get('col') not in used_indexes:
                    _cols = idx.get('col')
                    if not isinstance(_cols, list):
                        _cols = [_cols]

                    used_indexes.append(_cols)
                    _indexes.append(
                        Index(idx.get('name'), *_cols)
                    )
        return primary_key, _indexes, used_indexes

    def _get_type(self, col_type, params={}, unsigned=False):
        """Map the type to valid Column Types.

        See: http://docs.sqlalchemy.org/en/latest/core/type_basics.html

        Arguments:
            col_type {string} -- Type of column

        Keyword Arguments:
            params {dict} -- Additional Column Options (default: {{}})
            unsigned {bool} -- If it is an unsigned integer or not (default: {False})

        Returns:
            TypeEngine
        """
        # Todo: Unsinged Integers, check if they work in mysql, postgresql etc
        # TODO: Check if vendor specific types like json, mediumint, etc work
        return_type = Text()

        if col_type == 'big_increments':
            return_type = BigInteger().with_variant(BIGINT(unsigned=True), 'mysql')
        elif col_type == 'big_integer':
            return_type = BigInteger().with_variant(BIGINT(unsigned=unsigned), 'mysql')
        elif col_type == 'binary':
            return_type = LargeBinary()
        elif col_type == 'boolean':
            return_type = Boolean()
        elif col_type == 'char':
            return_type = CHAR(params.get('length'))
        elif col_type == 'date':
            return_type = Date()
        elif col_type == 'datetime':
            return_type = DateTime()
        elif col_type == 'decimal':
            return_type = Numeric(precision=params.get('precision'), scale=params.get('scale'))
        elif col_type == 'double':
            return_type = DOUBLE(
                precision=params.get('precision'),
                scale=params.get('scale')
            ).with_variant(
                Float(params.get('precision'), decimal_return_scale=params.get('scale')), 'sqlite'
            )
        elif col_type == 'enum':
            return_type = Enum(*params.get('fields', []))
        elif col_type == 'float':
            # ! Seems not to work, don't know why???
            return_type = Float(params.get('precision'), decimal_return_scale=params.get('scale'))
        elif col_type == 'increments':
            return_type = INTEGER(unsigned=True)
        elif col_type == 'integer':
            return_type = INTEGER(unsigned=unsigned)
        elif col_type == 'json':
            return_type = JSON(none_as_null=True).with_variant(Text, 'sqlite')
        elif col_type == 'long_text':
            return_type = LONGTEXT().with_variant(Text, 'sqlite')
        elif col_type == 'medium_integer':
            return_type = MEDIUMINT().with_variant(INTEGER(unsigned=unsigned), 'sqlite')
        elif col_type == 'medium_text':
            return_type = MEDIUMTEXT().with_variant(Text, 'sqlite')
        elif col_type == 'small_integer':
            return_type = SmallInteger()
        elif col_type == 'string':
            return_type = String(length=params.get('length'))
        elif col_type == 'text':
            return_type = Text()
        elif col_type == 'time':
            return_type = Time()
        elif col_type == 'timestamp':
            return_type = TIMESTAMP()
        elif col_type == 'array':
            arr_type = self._get_type(params.get('arr_type', 'text'))
            return_type = arr_type.with_variant(
                ARRAY(arr_type, dimensions=params.get('dimensions')),
                'postgresql'
            )

        return return_type
