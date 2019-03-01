"""Column factory class to create new columns.

Used to create new columns, indexes and foreign keys
with the help of sqlalchemy.
"""
from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, DOUBLE, LONGTEXT, MEDIUMINT, MEDIUMTEXT
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import ARRAY, BigInteger, Integer, Boolean, Date, DateTime, Enum,\
    LargeBinary, Numeric, SmallInteger, String, Text, Time, CHAR, Float, JSON, TIMESTAMP


def get_number_type(col_type, params, unsigned=False):
    """Create a number type column.

    Args:
        col_type (string): Type of the column.
        params (object): Additional parameters.
        unsigned (bool, optional): Defaults to False. Whether or not it is an unsigned int.

    Returns:
        sqlalchemy.types.TypeEngine: Number type like integer or float
    """
    # Todo: Unsinged Integers, check if they work in mysql, postgresql etc
    unsigned = True if col_type == 'big_increments' or col_type == 'increments' else unsigned

    # Integers
    if col_type == 'big_increments' or col_type == 'big_integer':
        return BigInteger()\
            .with_variant(BIGINT(unsigned=unsigned), 'mysql')\
            .with_variant(Integer(), 'sqlite')
    elif col_type == 'increments' or col_type == 'integer':
        return Integer().with_variant(INTEGER(unsigned=unsigned), 'mysql')
    # Floats
    elif col_type == 'float':
        # ! Seems not to work, don't know why???
        return Float(params.get('precision'), decimal_return_scale=params.get('scale'))
    elif col_type == 'decimal':
        return Numeric(precision=params.get('precision'), scale=params.get('scale'))
    elif col_type == 'double':
        return DOUBLE(
            precision=params.get('precision'),
            scale=params.get('scale')
        ).with_variant(
            Float(params.get('precision'), decimal_return_scale=params.get('scale')), 'sqlite'
        )
    elif col_type == 'medium_integer':
        return MEDIUMINT().with_variant(INTEGER(unsigned=unsigned), 'sqlite')
    elif col_type == 'small_integer':
        return SmallInteger()


def get_string_type(col_type, params):
    """Create a string type column.

    Args:
        col_type (string): Type of the column.
        params (object): Additional parameters.

    Returns:
        sqlalchemy.types.TypeEngine: String type like char or text
    """
    if col_type == 'char':
        return CHAR(params.get('length'))
    elif col_type == 'json':
        return (
            JSON(none_as_null=True)
            .with_variant(JSONB(none_as_null=True), 'postgresql')
            .with_variant(Text(), 'sqlite')
        )
    elif col_type == 'long_text':
        return LONGTEXT().with_variant(Text(), 'sqlite')
    elif col_type == 'medium_text':
        return MEDIUMTEXT().with_variant(Text(), 'sqlite')
    elif col_type == 'string':
        return String(length=params.get('length'))
    elif col_type == 'text':
        return Text()


def get_time_type(col_type):
    """Create a time type column.

    Args:
        col_type (string): Type of the column.

    Returns:
        sqlalchemy.types.TypeEngine: Time type like date or timestamp
    """
    if col_type == 'date':
        return Date()
    elif col_type == 'datetime':
        return DateTime()
    elif col_type == 'time':
        return Time()
    elif col_type == 'timestamp':
        return TIMESTAMP()


class ColumnFactory(object):

    """Factory class to create SQLAlchemy Columns."""

    @staticmethod
    def get_indexes(col, indexes, used_indexes=None):
        """Get all indexes and primary keys of a column.

        Args:
            col (Column): The column
            indexes (list): List of indexes
            used_indexes (list, optional): Defaults to None. Used indexes cols for composite keys.

        Returns:
            tuple: with primary keys, indexes and used indexes
        """
        used_indexes = [] if used_indexes is None else used_indexes
        _indexes = []
        primary_key = False

        for idx in indexes:
            idx_type = idx.get('type')
            idx_cols = idx.get('col')

            if idx_cols == col.get('name') or col.get('name') in idx_cols:
                # Primary Key
                if idx_type == 'primary':
                    primary_key = True
                # Indexes
                elif idx_type == 'unique' or idx_type == 'index' and idx_cols not in used_indexes:
                    if not isinstance(idx_cols, list):
                        idx_cols = [idx_cols]

                    used_indexes.extend(idx_cols)
                    _indexes.append(
                        Index(idx.get('name'), *idx_cols, unique=idx_type == 'unique')
                    )

        return primary_key, _indexes, used_indexes

    def get_columns_and_indexes(self, blueprint):
        """Get Column and Index instances from the blueprint.

        Args:
            blueprint (Blueprint): Schema Blueprint to add/modify table.

        Returns:
            dict: dictionary with columns and indexes
        """
        # Collection of columns and indexes
        used_indexes = []
        data = {
            'columns': [],
            'indexes': [],
        }

        for col in blueprint.columns:
            # Get Indexes and Primary Keys
            primary, indexes, _used_idxs = self.get_indexes(col, blueprint.indexes, used_indexes)
            data['indexes'].extend(indexes)
            used_indexes.extend(_used_idxs)

            # Add Foreign Key column
            foreign_key = self.get_foreign_key(col, blueprint.fkeys)
            if foreign_key is not False:
                data['columns'].append(foreign_key)
                continue

            # Add Column
            data['columns'].append(Column(
                col.get('name'),
                self.get_type(
                    col.get('type'),
                    col.get('parameters'),
                    unsigned=col.get('unsigned')
                ),
                default=col.get('default'),
                nullable=col.get('null'),
                autoincrement=col.get('parameters', {}).get('autoincrement', 'auto'),
                primary_key=primary,
            ))

        return data

    def create_foreign_key(self, key, col):
        """Create a foreign key column.

        Arguments:
            key (ForeignKey): Foreign Key
            col (Column): column to create foreign key on

        Returns:
            sqlalchemy.schema.Column: foreign key column
        """
        fkey = ForeignKey(
            key.get('ref_table') + '.' + key.get('ref_column'),
            ondelete=key.get('on_delete'),
            onupdate=key.get('on_update'),
            name=key.get('name')
        )

        return Column(
            col.get('name'),
            self.get_type(
                col.get('type'),
                col.get('parameters'),
                unsigned=col.get('unsigned')
            ),
            fkey,
            default=col.get('default'),
            nullable=col.get('null'),
            autoincrement=col.get('autoincrement', False)
        )

    def get_foreign_key(self, col, fkeys):
        """Get a foreign key from a column.

        Args:
            col (Column): Column to get foreign key of.
            fkeys (list): List of foreign keys

        Returns:
            sqlalchemy.schema.Column, False: either a foreign key column if found or False
        """
        col_name = col.get('name')
        foreign_key = [
            self.create_foreign_key(fkey.get('key'), col)
            for fkey in fkeys
            if fkey.get('col') == col_name  # or col_name in fkey.get('col')
        ]

        if len(foreign_key):
            return foreign_key[0]

        return False

    def get_type(self, col_type, params=None, unsigned=False):
        """Map the type to valid Column Types.

        Notes:
            http://docs.sqlalchemy.org/en/latest/core/type_basics.html

        Args:
            col_type (str): Type of column
            params (dict, optional): Defaults to None. Additional Column Options.
            unsigned (bool, optional): Defaults to False. If it is an unsigned integer or not.

        Returns:
            sqlalchemy.types.TypeEngine: Type for new column
        """
        # TODO: Check if vendor specific types like json, mediumint, etc work
        params = {} if params is None else params

        # Get number types
        if (
            'integer' in col_type or 'increments' in col_type or col_type == 'decimal' or
            col_type == 'double' or col_type == 'float'
        ):
            return get_number_type(col_type, params, unsigned)
        # Get String types
        elif (
            'text' in col_type or col_type == 'char' or col_type == 'json' or col_type == 'string'
        ):
            return get_string_type(col_type, params)
        # Get Date/Time Types
        elif 'date' in col_type or 'time' in col_type:
            return get_time_type(col_type)
        # Get BINARY type
        elif col_type == 'binary':
            return LargeBinary()
        # Get Boolean type
        elif col_type == 'boolean':
            return Boolean()
        # Get Enum Type
        elif col_type == 'enum':
            return Enum(*params.get('fields', []))
        # Get Array type
        elif col_type == 'array':
            arr_type = self.get_type(params.get('arr_type', 'text'))
            return arr_type.with_variant(
                ARRAY(arr_type, dimensions=params.get('dimensions')),
                'postgresql'
            )

        return Text()
