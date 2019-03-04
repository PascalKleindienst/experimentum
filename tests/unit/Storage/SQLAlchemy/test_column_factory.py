from experimentum.Storage.SQLAlchemy import ColumnFactory
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, DOUBLE, LONGTEXT, MEDIUMINT, MEDIUMTEXT
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Date, DateTime, Enum, Integer,\
    LargeBinary, Numeric, SmallInteger, String, Text, Time, CHAR, Float, JSON, TIMESTAMP
import pytest

invalid_types = [
    'invalid_integer', 'invalid_text', 'invalid_time'
]

integer_types = [
    {'id': 'big_increments', 'unsigned': True, 'mapping': BIGINT, 'impl': BigInteger},
    {'id': 'big_integer', 'unsigned': False, 'mapping': BIGINT, 'impl': BigInteger},
    {'id': 'increments', 'unsigned': True, 'mapping': INTEGER, 'impl': Integer},
    {'id': 'integer', 'unsigned': False, 'mapping': INTEGER, 'impl': Integer},
]

sqlite_variants = [
    {'id': 'json', 'sqlite': Text, 'impl': JSON},
    {'id': 'long_text', 'sqlite': Text, 'impl': LONGTEXT},
    {'id': 'medium_integer', 'sqlite': INTEGER, 'impl': MEDIUMINT},
    {'id': 'medium_text', 'sqlite': Text, 'impl': MEDIUMTEXT},
]

column_types = [
    {'id': 'binary', 'impl': LargeBinary},
    {'id': 'boolean', 'impl': Boolean},
    {'id': 'date', 'impl': Date},
    {'id': 'datetime', 'impl': DateTime},
    {'id': 'small_integer', 'impl': SmallInteger},
    {'id': 'text', 'impl': Text},
    {'id': 'time', 'impl': Time},
    {'id': 'timestamp', 'impl': TIMESTAMP},
    {'id': 'foobar does not exist', 'impl': Text}
]

attr_types = [
    {'id': 'char', 'impl': CHAR, 'attrs': {'length': 42}},
    {'id': 'string', 'impl': String, 'attrs': {'length': 42}},
    {'id': 'enum', 'impl': Enum, 'attrs': {'enums': ['foo', 'bar']}},
    {'id': 'decimal', 'impl': Numeric, 'attrs': {'precision': 10, 'scale': 2}},
    {'id': 'float', 'impl': Float, 'params': {'precision': 10, 'decimal_return_scale': 2}, 'attrs': {'precision': 10, 'scale': 2}}
]


class TestColumnFactory(object):

    @pytest.mark.parametrize('invalid_type', invalid_types)
    def test_invalid_type_mapping(self, invalid_type):
        factory = ColumnFactory()
        assert factory.get_type(invalid_type) is None

    @pytest.mark.parametrize('integer_type', integer_types)
    def test_integer_type_mapping(self, integer_type):
        factory = ColumnFactory()

        _type = factory.get_type(integer_type['id']).__dict__
        assert _type['mapping']['mysql'].unsigned is integer_type['unsigned']
        assert isinstance(_type['mapping']['mysql'], integer_type['mapping'])
        assert isinstance(_type['impl'], integer_type['impl'])

    @pytest.mark.parametrize('variants', sqlite_variants)
    def test_sqlite_variants_mappings(self, variants):
        factory = ColumnFactory()

        _type = factory.get_type(variants['id']).__dict__
        assert isinstance(_type['mapping']['sqlite'], variants['sqlite'])
        assert isinstance(_type['impl'], variants['impl'])

    @pytest.mark.parametrize('column_type', column_types)
    def test_type_mapping(self, column_type):
        factory = ColumnFactory()
        isinstance(factory.get_type(column_type['id']), column_type['impl'])

    @pytest.mark.parametrize('attr_type', attr_types)
    def test_attr_type_mapping(self, attr_type):
        factory = ColumnFactory()

        _type = factory.get_type(attr_type['id'], attr_type.get('attrs', {}))
        assert isinstance(_type, attr_type['impl'])

        for key, val in attr_type.get('params', {}).items():
            assert _type.__dict__[key] == val

    def test_double_type_mapping(self):
        factory = ColumnFactory()

        _type = factory.get_type('double', {'precision': 10, 'scale': 2}).__dict__
        assert _type['mapping']['sqlite'].precision == 10
        assert _type['mapping']['sqlite'].decimal_return_scale == 2
        assert _type['impl'].precision == 10
        assert _type['impl'].scale == 2
        assert isinstance(_type['mapping']['sqlite'], Float)
        assert isinstance(_type['impl'], DOUBLE)

    def test_array_type_mapping(self):
        factory = ColumnFactory()
        _type = factory.get_type('array', {'arr_type': 'integer', 'dimensions': 2}).__dict__
        assert isinstance(_type['mapping']['postgresql'], ARRAY)
        # assert isinstance(_type['mapping']['postgresql'].__dict__['item_type']['impl'], INTEGER)
        assert _type['mapping']['postgresql'].__dict__['dimensions'] is 2
        assert isinstance(_type['impl'], Integer)
