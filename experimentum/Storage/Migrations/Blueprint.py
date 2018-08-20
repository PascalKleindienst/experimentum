r"""The :py:class:`.Blueprint` class lets you create, delete, or alter columns of a table.

Columns
=======

Adding Columns
--------------
To update an existing table, you can use the :py:meth:`.Schema.table` method.
The method accepts a table name as its argument and returns a :py:class:`.Blueprint`
instance that can be used to add columns to the table::

    with self.schema.table('users') as table:
        table.string('email')
        table.string('address').nullable()
        table.integer('age').nullable().unsigned()

The table builder contains a plethora of column types that you can use when building your tables:

+-------------------------------------------+------------------------------------------------------+
| Command                                   | Description                                          |
+===========================================+======================================================+
| ``table.array('ratings', 'integer', 2)``  | ARRAY column type. Only supported in **postgresql**! |
+-------------------------------------------+------------------------------------------------------+
| ``table.big_increments('id')``            | Auto-incrementing ID using a "big integer" (primary  |
|                                           | key) equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.big_integer('votes)``             | BIGINT equivalent column.                            |
+-------------------------------------------+------------------------------------------------------+
| ``table.binary('data')``                  | BLOB equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.boolean('confirmed')``            | BOOLEAN equivalent column.                           |
+-------------------------------------------+------------------------------------------------------+
| ``table.char('name', 4)``                 | CHAR equivalent column with a length.                |
+-------------------------------------------+------------------------------------------------------+
| ``table.date('created_on')``              | DATE equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.datetime('created_at')``          | DATETIME equivalent column.                          |
+-------------------------------------------+------------------------------------------------------+
| ``table.decimal('amount', 5, 2)``         | DECIMAL equivalent column with a precision           |
|                                           | *(total digits)* and a scale *(decimal digits)*.     |
+-------------------------------------------+------------------------------------------------------+
| ``table.double('column', 15, 8)``         | DOUBLE equivalent column with a precision            |
|                                           | *(total digits)* and a scale *(decimal digits)*.     |
+-------------------------------------------+------------------------------------------------------+
| ``table.enum('choices', ['foo', 'bar'])`` | ENUM equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.float('amount')``                 | FLOAT equivalent column.                             |
+-------------------------------------------+------------------------------------------------------+
| ``table.increments('id')``                | Auto-incrementing ID using a "integer" (primary key) |
|                                           | equivalent column.                                   |
+-------------------------------------------+------------------------------------------------------+
| ``table.integer('votes')``                | INTEGER equivalent column.                           |
+-------------------------------------------+------------------------------------------------------+
| ``table.json('options')``                 | JSON equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.long_text('description')``        | LONGTEXT equivalent column.                          |
+-------------------------------------------+------------------------------------------------------+
| ``table.medium_integer('votes')``         | MEDIUMINT equivalent column.                         |
+-------------------------------------------+------------------------------------------------------+
| ``table.medium_text('description')``      | MEDIUMTEXT equivalent column.                        |
+-------------------------------------------+------------------------------------------------------+
| ``table.small_integer('votes')``          | SMALLINT equivalent column.                          |
+-------------------------------------------+------------------------------------------------------+
| ``table.string('email')``                 | VARCHAR equivalent column.                           |
+-------------------------------------------+------------------------------------------------------+
| ``table.string('votes', 100)``            | VARCHAR equivalent column with a length.             |
+-------------------------------------------+------------------------------------------------------+
| ``table.text('description')``             | TEXT equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.time('sunrise')``                 | TIME equivalent column.                              |
+-------------------------------------------+------------------------------------------------------+
| ``table.timestamp('added_at')``           | TIMESTAMP equivalent column.                         |
+-------------------------------------------+------------------------------------------------------+

Column Modifiers
----------------
Each of the column methods above returns a :py:class:`.Column` instance, which lets you add several
column "modifier" while adding a column to a table. For example, to make a column "nullable" you can
use the :py:meth:`~.Column.nullable` method::

    with self.schema.table('users') as table:
        table.string('email').nullable()

The column modifiers are the following *(does not include index modifiers)*:

=============================  ==============================================
Modifier                       Description
=============================  ==============================================
``.default('default_value')``  Specify a default value for the column.
``.nullable()``                Designate that the column allows NULL values.
``.unsigned()``                Set INTEGER column as UNSINGED *(MySQL)*.
=============================  ==============================================

Dropping Columns
----------------
To drop a column from a table, you can use the :py:meth:`~.Blueprint.drop_column`
method.

Dropping a column from a database table::

    with self.schema.table('users') as table:
        table.drop_column('votes')

Dropping multiple columns from a database table::

    with self.schema.table('users') as table:
        table.drop_column('votes', 'avatar', 'location')

Indexes
=======
The schema builder supports several types of indexes which you can add to and/or drop from columns.
You can create the index after defining the column. For example::

    table.string('email')
    table.unique('email')

Available Index Types
---------------------
Each index method accepts an optional second argument to specify the name of the index.
If omitted, the name will be derived from the names of the table and column(s).
Below is a list of all available index types:

======================================  =====================
Command                                 Description
======================================  =====================
``table.primary('id')``                 Addys a primary key.
``table.primary(['id', 'parent_id'])``  Adds composite keys.
``table.unique('email)``                Adds a unique index.
``table.index('state')``                Adds a basic index.
======================================  =====================

.. note::
    In ``MySQL``/``MariaDB`` and ``PostgreSQL`` the length of indexes are limited.
    experimentum generates index names based on table and column names, therefore if
    your column names are too long you can pass the ``name`` keyword argument to specify
    your own index name::

        table.index(
            ['some_field_with_a_really_long_name', 'another_really_long_field'],
            name='my_idx_name'
        )

Dropping Indexes
----------------
To drop an index you must specify the index's columns. experimentum assigns a reasonable
name to the indexes by default. If you have specified a custom index name, you have to add
it as the optional second argument.

=================================  =============================================
Command                            Description
=================================  =============================================
``table.drop_primary('id')``       Drop a primary key from the "id" column.
``table.drop_unique('email)``      Drop a unique index from the "email" column.
``table.drop_index('state')``      Drop a basic index from the "state" column.
``table.drop_foreign('user_id')``  Drop a foreign key from the "user_id" column.
=================================  =============================================


Foreign Key Contraints
======================
experimentum also provides support for adding foreign key constraints to your tables::

    with self.schema.table('posts') as table:
        table.increments('user_id')
        table.foreign('user_id')\
            .references('id').on('users')\
            .on_delete('cascade')\
            .on_update('cascade')

In this example, we are stating that the ``user_id`` column references the ``id`` column
on the ``users`` table and set the "on update" and "on delete" actions to ``cascade``.
Make sure to create the foreign key column first!

To drop a foreign key, you can use the :py:meth:`~.Blueprint.drop_foreign` method. It works
just like dropping an index.
"""
from experimentum.Storage.Migrations import Column, ForeignKey


class Blueprint(object):

    """Lets you create, delete, or alter columns of a table.

    Inspired by the Lavavel Schema Blueprint
    (https://laravel.com/docs/5.6/migrations#columns).

    Attributes:
        table (str): Name of the table.
        columns (list): Defaults to []. List of columns for the table.
        dropped (object): Defaults to {'columns': [], 'indexes': []}. Object with list of dropped
                        columns and indexes of the table.
        indexes (list): Defaults to []. List of indices for the table.
        fkeys (list): Defaults to []. List of foreign keys for the table.
        action (str): Defaults to 'alter'. Action (i.e. create or alter).
    """

    def __init__(self, table):
        """Initialize the blueprint.

        Args:
            table (str): Name of the table.
        """
        self.table = table
        self.columns = []
        self.dropped = {'columns': [], 'indexes': []}
        self.indexes = []
        self.fkeys = []
        self.action = 'alter'

    def create(self):
        """Set the create action."""
        self.action = 'create'

    ###############
    # * Columns * #
    ###############
    def add_column(self, col_type, name, **kwargs):
        """Add a new column to the blueprint.

        Args:
            col_type (str): Column Type
            name (str): Name of the Column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        col = Column(col_type, name, kwargs)
        self.columns.append(col)
        return col

    def drop_column(self, *args):
        """Drop one or multiple columns.

        Args:
            *args (str): Column names
        """
        self.dropped['columns'].extend(list(args))

    def array(self, column, arr_type, dimensions=None):
        """ARRAY column type.

        Only supported in **postgresql**, for other systems it defaults back to `arr_type`!

        Args:
            column (str): Name of the column.
            arr_type (str): Type of array
            dimensions (int, optional): Defaults to None. Array Dimension.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('array', column, arr_type=arr_type, dimensions=dimensions)

    def big_increments(self, column):
        """Auto-incrementing ID using a "big integer" (primary key) equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('big_integer', column, autoincrement=True)

    def big_integer(self, column):
        """BIGINT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('big_integer', column)

    def binary(self, column):
        """BLOB equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('binary', column)

    def boolean(self, column):
        """BOOLEAN equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('boolean', column)

    def char(self, column, length):
        """CHAR equivalent column with a length.

        Args:
            column (str): Name of the column.
            length (int): Length of the column

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('char', column, length=length)

    def date(self, column):
        """DATE equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('date', column)

    def datetime(self, column):
        """DATETIME equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('datetime', column)

    def decimal(self, column, precision, scale=2):
        """DECIMAL equivalent column with a precision (total digits) and a scale (decimal digits).

        Args:
            column (str): Name of the column.
            precision (int): Total Digits
            scale (int, optional): Defaults to 2. Number of decimal gigits

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('decimal', column, precision=precision, scale=scale)

    def double(self, column, precision, scale=2):
        """DOUBLE equivalent column with a precision (total digits) and a scale (decimal digits).

        Args:
            column (str): Name of the column.
            precision (int): Total Digits
            scale (int): Default to 2. Number of decimal digits.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('double', column, precision=precision, scale=scale)

    def enum(self, column, fields):
        """ENUM equivalent column.

        Args:
            column (str): Name of the column.
            fields (list): Field Names for the enum

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('enum', column, fields=fields)

    def float(self, column):
        """FLOAT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('float', column)

    def increments(self, column):
        """Auto-incrementing ID using a "integer" (primary key) equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('integer', column, autoincrement=True)

    def integer(self, column):
        """INTEGER equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('integer', column)

    def json(self, column):
        """JSON equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('json', column)

    def long_text(self, column):
        """LONGTEXT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('long_text', column)

    def medium_integer(self, column):
        """MEDIUMINT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('medium_integer', column)

    def medium_text(self, column):
        """MEDIUMTEXT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('medium_text', column)

    def small_integer(self, column):
        """SMALLINT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('small_integer', column)

    def string(self, column, length=None):
        """VARCHAR equivalent column with an optional length.

        Args:
            column (str): Name of the column.
            length (int, optional): Defaults to None. Length of the string.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('string', column, length=length)

    def text(self, column):
        """TEXT equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('text', column)

    def time(self, column):
        """TIME equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('time', column)

    def timestamp(self, column):
        """TIMESTAMP equivalent column.

        Args:
            column (str): Name of the column.

        Returns:
            Column: Column data structure to add column modifiers.
        """
        return self.add_column('timestamp', column)

    ###############
    # * Indexes * #
    ###############
    def primary(self, column, name=None):
        """Add a primary key to the column.

        Args:
            column (str): Primary Key column
            name (str, optional): Default to None. Name of the primary key.

        Returns:
            Blueprint: self instance for method chaining.
        """
        self._add_idx(column, 'primary', name)
        return self

    def unique(self, column, name=None):
        """Add a unique key to the column.

        Args:
            column (str): Unique Key column
            name (str, optional): Default to None. Name of the unique key.

        Returns:
            Blueprint: self instance for method chaining.
        """
        self._add_idx(column, 'unique', name)
        return self

    def index(self, column, name=None):
        """Add a basic index to the column.

        Args:
            column (str): Indexed column
            name (str, optional): Default to None. Name of the unique key.

        Returns:
            Blueprint: self instance for method chaining.
        """
        self._add_idx(column, 'index', name)
        return self

    def foreign(self, column, name=None):
        """Add a foreign key to the column.

        Args:
            column (str): Foreign Key column
            name (str, optional): Default to None. Name of the foreign key.

        Returns:
            ForeignKey: ForeignKey data structure to configure foreign key.
        """
        if not name:
            name = '{}_{}_{}'.format(self.table, column, 'foreign')

        fkey = ForeignKey(column, name)
        self.fkeys.append({'col': column, 'key': fkey})
        return fkey

    def _add_idx(self, column, idx_type, name=None):
        """Add an index to the index list.

        Args:
            column (str): indexed column.
            idx_type (str): Type of the index.
            name (str, optional): Default to None. Custom index name.
        """
        if not name:
            name = '{}_{}_{}'.format(self.table, column, idx_type)

        self.indexes.append({
            'col': column,
            'type': idx_type,
            'name': name
        })

    def drop_primary(self, column, name=None):
        """Drop a primary key from the column.

        Args:
            column (str): Primary Key column
            name (str, optional): Default to None. Name of the primary key.
        """
        self._drop_idx(column, 'primary', name)

    def drop_unique(self, column, name=None):
        """Drop a unique key from the column.

        Args:
            column (str): unique Key column
            name (str, optional): Default to None. Name of the unique key.
        """
        self._drop_idx(column, 'unique', name)

    def drop_index(self, column, name=None):
        """Drop a index key from the column.

        Args:
            column (str): index Key column
            name (str, optional): Default to None. Name of the index key.
        """
        self._drop_idx(column, 'index', name)

    def drop_foreign(self, column, name=None):
        """Drop a foreign key from the column.

        Args:
            column (str): foreign Key column
            name (str, optional): Default to None. Name of the foreign key.
        """
        self._drop_idx(column, 'foreign', name)

    def _drop_idx(self, column, idx_type, name=None):
        """Drop an index.

        Args:
            column (str): indexed column
            idx_type (str): Type of the index.
            name (str, optional): Default to None. Custom index name.
        """
        if not name:
            name = '{}_{}_{}'.format(self.table, column, idx_type)

        self.dropped['indexes'].append({
            'col': column,
            'type': idx_type,
            'name': name
        })
