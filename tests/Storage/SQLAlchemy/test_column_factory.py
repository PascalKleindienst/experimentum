from experimentum.Storage.SQLAlchemy import ColumnFactory
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, DOUBLE, LONGTEXT, MEDIUMINT, MEDIUMTEXT
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Date, DateTime, Enum, Integer,\
    LargeBinary, Numeric, SmallInteger, String, Text, Time, CHAR, Float, JSON, TIMESTAMP


class TestColumnFactory(object):
    def test_type_mapping(self, mocker):
        factory = ColumnFactory()

        _type = factory.get_type('big_increments').__dict__
        assert _type['mapping']['mysql'].unsigned == True
        assert isinstance(_type['mapping']['mysql'], BIGINT)
        assert isinstance(_type['impl'], BigInteger)

        _type = factory.get_type('big_integer', unsigned=False).__dict__
        assert _type['mapping']['mysql'].unsigned is False
        assert isinstance(_type['mapping']['mysql'], BIGINT)
        assert isinstance(_type['impl'], BigInteger)

        _type = factory.get_type('double', {'precision': 10, 'scale': 2}).__dict__
        assert _type['mapping']['sqlite'].precision == 10
        assert _type['mapping']['sqlite'].decimal_return_scale == 2
        assert _type['impl'].precision == 10
        assert _type['impl'].scale == 2
        assert isinstance(_type['mapping']['sqlite'], Float)
        assert isinstance(_type['impl'], DOUBLE)

        self._test_get_type_attribute(factory, 'char', CHAR, {'length': 42}, {'length': 42})
        self._test_get_type_attribute(factory, 'string', String, {'length': 42}, {'length': 42})
        self._test_get_type_attribute(factory, 'enum', Enum, {'enums': ['foo', 'bar']}, {'fields': ['foo', 'bar']})
        self._test_get_type_attribute(factory, 'integer', Integer, {'unsigned': False})
        self._test_get_type_attribute(factory, 'increments', Integer, {'unsigned': True})
        self._test_get_type_attribute(factory, 'decimal', Numeric, {'precision': 10, 'scale': 2}, {'precision': 10, 'scale': 2})
        self._test_get_type_attribute(factory, 'float', Float, {'precision': 10, 'decimal_return_scale': 2}, {'precision': 10, 'scale': 2})

        self._test_get_type_sqlite_variant(factory, 'json', Text, JSON)
        self._test_get_type_sqlite_variant(factory, 'long_text', Text, LONGTEXT)
        self._test_get_type_sqlite_variant(factory, 'medium_integer', INTEGER, MEDIUMINT)
        self._test_get_type_sqlite_variant(factory, 'medium_text', Text, MEDIUMTEXT)

        _type = factory.get_type('array', {'arr_type': 'integer', 'dimensions': 2}).__dict__
        assert isinstance(_type['mapping']['postgresql'], ARRAY)
        assert isinstance(_type['mapping']['postgresql'].__dict__['item_type'], INTEGER)
        assert _type['mapping']['postgresql'].__dict__['dimensions'] is 2
        assert isinstance(_type['impl'], Integer)

        assert isinstance(factory.get_type('binary'), LargeBinary)
        assert isinstance(factory.get_type('boolean'), Boolean)
        assert isinstance(factory.get_type('date'), Date)
        assert isinstance(factory.get_type('datetime'), DateTime)
        assert isinstance(factory.get_type('small_integer'), SmallInteger)
        assert isinstance(factory.get_type('text'), Text)
        assert isinstance(factory.get_type('time'), Time)
        assert isinstance(factory.get_type('timestamp'), TIMESTAMP)

        assert isinstance(factory.get_type('foobar does not exist'), Text)

    def _test_get_type_attribute(self, factory, type_key, impl, attrs, parameters={}):
        _type = factory.get_type(type_key, parameters)
        assert isinstance(_type, impl)

        for attr_key, attr_val in attrs.items():
            assert _type.__dict__[attr_key] == attr_val

    def _test_get_type_sqlite_variant(self, factory, type_key, sqlite_type, impl_type):
        _type = factory.get_type(type_key).__dict__
        assert isinstance(_type['mapping']['sqlite'], sqlite_type)
        assert isinstance(_type['impl'], impl_type)