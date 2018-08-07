from experimentum.Storage.Migrations import Blueprint


class TestBlueprint(object):
    def test_init(self):
        blueprint = Blueprint('some table')
        assert blueprint.table is 'some table'
        assert blueprint.columns == []
        assert blueprint.indexes == []
        assert blueprint.action is None

    # * COLUMNS *
    def test_create_action(self):
        blueprint = Blueprint('some table')
        blueprint.create()
        assert blueprint.action is 'create'

    def test_add_column(self):
        blueprint = Blueprint('some table')
        blueprint.add_column('col_type', 'name', foo='bar')
        col = blueprint.columns[-1]
        assert col.get('type') is 'col_type'
        assert col.get('name') is 'name'
        assert col.get('parameters') == {'foo': 'bar'}

    def test_add_array_column(self):
        blueprint = Blueprint('some table')
        blueprint.array('col_name', 'arr_type', dimensions=2)
        col = blueprint.columns[-1]
        assert col.get('type') is 'array'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'arr_type': 'arr_type', 'dimensions': 2}

    def test_add_big_increments(self):
        blueprint = Blueprint('some table')
        blueprint.big_increments('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'big_integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'autoincrement': True}

    def test_add_big_integer(self):
        blueprint = Blueprint('some table')
        blueprint.big_integer('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'big_integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_binary(self):
        blueprint = Blueprint('some table')
        blueprint.binary('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'binary'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_boolean(self):
        blueprint = Blueprint('some table')
        blueprint.boolean('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'boolean'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_char(self):
        blueprint = Blueprint('some table')
        blueprint.char('col_name', 4)
        col = blueprint.columns[-1]
        assert col.get('type') is 'char'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'length': 4}

    def test_add_date(self):
        blueprint = Blueprint('some table')
        blueprint.date('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'date'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_datetime(self):
        blueprint = Blueprint('some table')
        blueprint.datetime('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'datetime'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_decimal(self):
        blueprint = Blueprint('some table')
        blueprint.decimal('col_name', 10, 4)
        col = blueprint.columns[-1]
        assert col.get('type') is 'decimal'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'precision': 10, 'scale': 4}

    def test_add_double(self):
        blueprint = Blueprint('some table')
        blueprint.double('col_name', 10, 4)
        col = blueprint.columns[-1]
        assert col.get('type') is 'double'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'precision': 10, 'scale': 4}

    def test_add_enum(self):
        blueprint = Blueprint('some table')
        blueprint.enum('col_name', ['a', 'b'])
        col = blueprint.columns[-1]
        assert col.get('type') is 'enum'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'fields': ['a', 'b']}

    def test_add_float(self):
        blueprint = Blueprint('some table')
        blueprint.float('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'float'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_increments(self):
        blueprint = Blueprint('some table')
        blueprint.increments('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'autoincrement': True}

    def test_add_integer(self):
        blueprint = Blueprint('some table')
        blueprint.integer('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_json(self):
        blueprint = Blueprint('some table')
        blueprint.json('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'json'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_long_text(self):
        blueprint = Blueprint('some table')
        blueprint.long_text('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'long_text'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_medium_integer(self):
        blueprint = Blueprint('some table')
        blueprint.medium_integer('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'medium_integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_medium_text(self):
        blueprint = Blueprint('some table')
        blueprint.medium_text('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'medium_text'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_small_integer(self):
        blueprint = Blueprint('some table')
        blueprint.small_integer('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'small_integer'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_string(self):
        blueprint = Blueprint('some table')
        blueprint.string('col_name', 42)
        col = blueprint.columns[-1]
        assert col.get('type') is 'string'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {'length': 42}

    def test_add_text(self):
        blueprint = Blueprint('some table')
        blueprint.text('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'text'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_time(self):
        blueprint = Blueprint('some table')
        blueprint.time('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'time'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    def test_add_timestamp(self):
        blueprint = Blueprint('some table')
        blueprint.timestamp('col_name')
        col = blueprint.columns[-1]
        assert col.get('type') is 'timestamp'
        assert col.get('name') is 'col_name'
        assert col.get('parameters') == {}

    # * Indices *