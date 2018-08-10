from experimentum.Storage.Migrations import Column, ForeignKey


class Blueprint(object):

    """Inspired by the Lavavel Schema Blueprint (https://laravel.com/docs/5.6/migrations#columns).

    Attributes:
        table {string} -- Name of the table
        columns {list} -- List of columns for the table (default: {[]})
        dropped {list} -- List of dropped columns of the table (default: {[]})
        indexes {list} -- List of indices for the table (default: {[]})
        fkeys {list} -- List of foreign keys for the table (default: {[]})
        action {string} -- Action (i.e. create or alter) (default: {'alter'})
    """

    def __init__(self, table):
        """Initialize the blueprint.

        Arguments:
            table {string} -- Name of the table
        """
        self.table = table
        self.columns = []
        self.dropped = []
        self.indexes = []
        self.fkeys = []
        self.action = 'alter'

    def create(self):
        """Set the create action."""
        self.action = 'create'

    """ Columns """
    def add_column(self, col_type, name, *args, **kwargs):
        """Add a new column to the blueprint.

        Arguments:
            col_type {string} -- Column Type
            name {string} -- Name of the Column

        Returns:
            Column
        """
        col = Column(col_type, name, kwargs)
        self.columns.append(col)
        return col

    def drop_column(self, *args):
        """Drop one or multiple columns.

        Arguments:
            *args {string} -- Column names
        """
        self.dropped.extend(list(args))

    def array(self, column, arr_type, dimensions=None):
        """ARRAY column type.

        Only supported in **postgresql**, for other systems it defaults back to `arr_type`!

        Arguments:
            column {string} -- Name of the column
            arr_type {string} -- Type of array

        Keyword Arguments:
            dimensions {int} -- Array Dimension (default: {None})

        Returns:
            Column
        """
        return self.add_column('array', column, arr_type=arr_type, dimensions=dimensions)

    def big_increments(self, column):
        """Auto-incrementing ID using a "big integer" (primary key) equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('big_integer', column, autoincrement=True)

    def big_integer(self, column):
        """BIGINT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('big_integer', column)

    def binary(self, column):
        """BLOB equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('binary', column)

    def boolean(self, column):
        """BOOLEAN equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('boolean', column)

    def char(self, column, length):
        """CHAR equivalent column with a length.

        Arguments:
            column {string} -- Name of the column
            length {int} -- Length of the column

        Returns:
            Column
        """
        return self.add_column('char', column, length=length)

    def date(self, column):
        """DATE equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('date', column)

    def datetime(self, column):
        """DATETIME equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('datetime', column)

    def decimal(self, column, precision, scale=2):
        """DECIMAL equivalent column with a precision (toal digits) and a scale (decimal digits).

        Arguments:
            column {string} -- Name of the column
            precision {int} -- Total Digits

        Keyword Arguments:
            scale {int} -- Decimal Digits (default: {2})

        Returns:
            Column
        """
        return self.add_column('decimal', column, precision=precision, scale=scale)

    def double(self, column, precision, scale=2):
        """DOUBLE equivalent column with a precision (toal digits) and a scale (decimal digits).

        Arguments:
            column {string} -- Name of the column
            precision {int} -- Total Digits

        Keyword Arguments:
            scale {int} -- Decimal Digits (default: {2})

        Returns:
            Column
        """
        return self.add_column('double', column, precision=precision, scale=scale)

    def enum(self, column, fields):
        """ENUM equivalent column.

        Arguments:
            column {string} -- Name of the column
            fields {list} -- Field Names for the enum

        Returns:
            Column
        """
        return self.add_column('enum', column, fields=fields)

    def float(self, column):
        """FLOAT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('float', column)

    def increments(self, column):
        """Auto-incrementing ID using a "integer" (primary key) equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('integer', column, autoincrement=True)

    def integer(self, column):
        """INTEGER equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('integer', column)

    def json(self, column):
        """JSON equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('json', column)

    def long_text(self, column):
        """LONGTEXT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('long_text', column)

    def medium_integer(self, column):
        """MEDIUMINT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('medium_integer', column)

    def medium_text(self, column):
        """MEDIUMTEXT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('medium_text', column)

    def small_integer(self, column):
        """SMALLINT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('small_integer', column)

    def string(self, column, length=None):
        """VARCHAR equivalent column with an optional length.

        Arguments:
            column {string} -- Name of the column

        Keyword Arguments:
            length {int} -- Length of the string (default: {None})

        Returns:
            Column
        """
        return self.add_column('string', column, length=length)

    def text(self, column):
        """TEXT equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('text', column)

    def time(self, column):
        """TIME equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('time', column)

    def timestamp(self, column):
        """TIMESTAMP equivalent column.

        Arguments:
            column {string} -- Name of the column

        Returns:
            Column
        """
        return self.add_column('timestamp', column)

    """ Indices """
    def primary(self, column, name=None):
        """Add a primary key to the column.

        Arguments:
            column {string} -- Primary Key column

        Keyword Arguments:
            name {string} -- Name of the primary key (default: {None})

        Returns:
            Blueprint
        """
        self._add_idx(column, 'primary', name)
        return self

    def unique(self, column, name=None):
        """Add a unique key to the column.

        Arguments:
            column {string} -- Unique Key column

        Keyword Arguments:
            name {string} -- Name of the unique key (default: {None})

        Returns:
            Blueprint
        """
        self._add_idx(column, 'unique', name)
        return self

    def index(self, column, name=None):
        """Add a basic index to the column.

        Arguments:
            column {string} -- Indexed column

        Keyword Arguments:
            name {string} -- Name of the unique key (default: {None})

        Returns:
            Blueprint
        """
        self._add_idx(column, 'index', name)
        return self

    def foreign(self, column, name=None):
        """Add a foreign key to the column.

        Arguments:
            column {string} -- Foreign Key column

        Keyword Arguments:
            name {string} -- Name of the foreign key (default: {None})

        Returns:
            ForeignKey
        """
        fkey = ForeignKey(column, name)
        self.fkeys.append({'col': column, 'key': fkey})
        return fkey

    def _add_idx(self, column, idx_type, name=None):
        """Add an index to the index list.

        Arguments:
            column {string} -- indexed column
            idx_type {string} -- index type

        Keyword Arguments:
            name {string} -- Custom index name (default: {None})
        """
        if not name:
            name = '{}_{}_{}'.format(self.table, column, idx_type)

        self.indexes.append({
            'col': column,
            'type': idx_type,
            'name': name
        })
