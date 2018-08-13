from experimentum.Storage.SQLAlchemy import Store
from experimentum.Storage.Migrations import Blueprint
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, inspect
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, DOUBLE, LONGTEXT, MEDIUMINT, MEDIUMTEXT
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Date, DateTime, Enum,\
    LargeBinary, Numeric, SmallInteger, String, Text, Time, CHAR, Float, JSON, TIMESTAMP


class TestStore(object):
    def _init_store(self, mocker):
        app = mocker.patch('experimentum.Experiments.App')
        engine = create_engine('sqlite:///')

        store = Store(app)
        store.set_engine(engine)

        return store

    def test_set_engine(self, mocker):
        app = mocker.patch('experimentum.Experiments.App')
        engine = create_engine('sqlite:///')

        store = Store(app)
        assert store.app == app

        store.set_engine(engine)
        assert store.engine is engine
        assert isinstance(store.meta, MetaData)

    def test_has_table(self, mocker):
        store = self._init_store(mocker)

        table = Table('foo', store.meta, Column('id', Integer))
        table.create(store.engine)
        assert store.has_table('foo') is True

        table.drop(store.engine)
        assert store.has_table('foo') is False

    def test_has_column(self, mocker):
        store = self._init_store(mocker)

        table = Table('foo', store.meta, Column('id', Integer))
        table.create(store.engine)
        assert store.has_column('foo', 'id') is True

        table.drop(store.engine)
        assert store.has_column('foo', 'id') is False

    def test_drop_table(self, mocker):
        store = self._init_store(mocker)

        table = Table('foo', store.meta, Column('id', Integer))
        table.create(store.engine)
        assert 'foo' in inspect(store.engine).get_table_names()

        store.drop('foo')
        assert 'foo' not in inspect(store.engine).get_table_names()

    def test_drop_if_exists_table(self, mocker):
        store = self._init_store(mocker)

        table = Table('foo', store.meta, Column('id', Integer))
        table.create(store.engine)
        assert 'foo' in inspect(store.engine).get_table_names()

        store.drop_if_exists('foo')
        assert 'foo' not in inspect(store.engine).get_table_names()

    def test_rename_table(self, mocker):
        store = self._init_store(mocker)

        table = Table('foo', store.meta, Column('id', Integer))
        table.create(store.engine)
        assert ['foo'] == inspect(store.engine).get_table_names()

        store.rename('foo', 'bar')
        assert ['bar'] == inspect(store.engine).get_table_names()

    def test_create_table(self, mocker):
        store = self._init_store(mocker)
        table = Table('users', store.meta, Column('id', Integer))
        table.create(store.engine)

        blueprint = Blueprint('foo')
        blueprint.add_column('integer', 'id')
        blueprint.primary('id')
        blueprint.add_column('integer', 'user_id')
        blueprint.foreign('user_id', 'fkey_name').references('id').on('users')

        blueprint.add_column('integer', 'unique_key')
        blueprint.unique('unique_key')
        blueprint.add_column('integer', 'some_key')
        blueprint.index('some_key')

        assert 'foo' not in inspect(store.engine).get_table_names()

        store.create(blueprint)
        inspector = inspect(store.engine)
        assert 'foo' in inspector.get_table_names()
        assert 'id' == inspector.get_columns('foo')[0]['name']
        assert 'fkey_name' == inspector.get_foreign_keys('foo')[1]['name']
        assert [
            {'unique': 0, 'name': u'foo_some_key_index', 'column_names': [u'some_key']},
            {'unique': 1, 'name': u'foo_unique_key_unique', 'column_names': [u'unique_key']}
        ] == inspector.get_indexes('foo')


    def test_type_mapping(self, mocker):
        store = self._init_store(mocker)

        _type = store._get_type('big_increments').__dict__
        assert _type['mapping']['mysql'].unsigned == True
        assert isinstance(_type['mapping']['mysql'], BIGINT)
        assert isinstance(_type['impl'], BigInteger)

        _type = store._get_type('big_integer', unsigned=False).__dict__
        assert _type['mapping']['mysql'].unsigned is False
        assert isinstance(_type['mapping']['mysql'], BIGINT)
        assert isinstance(_type['impl'], BigInteger)

        _type = store._get_type('double', {'precision': 10, 'scale': 2}).__dict__
        assert _type['mapping']['sqlite'].precision == 10
        assert _type['mapping']['sqlite'].decimal_return_scale == 2
        assert _type['impl'].precision == 10
        assert _type['impl'].scale == 2
        assert isinstance(_type['mapping']['sqlite'], Float)
        assert isinstance(_type['impl'], DOUBLE)

        self._test_get_type_attribute(store, 'char', CHAR, {'length': 42}, {'length': 42})
        self._test_get_type_attribute(store, 'string', String, {'length': 42}, {'length': 42})
        self._test_get_type_attribute(store, 'enum', Enum, {'enums': ['foo', 'bar']}, {'fields': ['foo', 'bar']})
        self._test_get_type_attribute(store, 'integer', Integer, {'unsigned': False})
        self._test_get_type_attribute(store, 'increments', Integer, {'unsigned': True})
        self._test_get_type_attribute(store, 'decimal', Numeric, {'precision': 10, 'scale': 2}, {'precision': 10, 'scale': 2})
        self._test_get_type_attribute(store, 'float', Float, {'precision': 10, 'decimal_return_scale': 2}, {'precision': 10, 'scale': 2})

        self._test_get_type_sqlite_variant(store, 'json', Text, JSON)
        self._test_get_type_sqlite_variant(store, 'long_text', Text, LONGTEXT)
        self._test_get_type_sqlite_variant(store, 'medium_integer', INTEGER, MEDIUMINT)
        self._test_get_type_sqlite_variant(store, 'medium_text', Text, MEDIUMTEXT)

        _type = store._get_type('array', {'arr_type': 'integer', 'dimensions': 2}).__dict__
        assert isinstance(_type['mapping']['postgresql'], ARRAY)
        assert isinstance(_type['mapping']['postgresql'].__dict__['item_type'], INTEGER)
        assert _type['mapping']['postgresql'].__dict__['dimensions'] is 2
        assert isinstance(_type['impl'], Integer)

        assert isinstance(store._get_type('binary'), LargeBinary)
        assert isinstance(store._get_type('boolean'), Boolean)
        assert isinstance(store._get_type('date'), Date)
        assert isinstance(store._get_type('datetime'), DateTime)
        assert isinstance(store._get_type('small_integer'), SmallInteger)
        assert isinstance(store._get_type('text'), Text)
        assert isinstance(store._get_type('time'), Time)
        assert isinstance(store._get_type('timestamp'), TIMESTAMP)

    def _test_get_type_attribute(self, store, type_key, impl, attrs, parameters={}):
        _type = store._get_type(type_key, parameters)
        assert isinstance(_type, impl)

        for attr_key, attr_val in attrs.items():
            assert _type.__dict__[attr_key] == attr_val

    def _test_get_type_sqlite_variant(self, store, type_key, sqlite_type, impl_type):
        _type = store._get_type(type_key).__dict__
        assert isinstance(_type['mapping']['sqlite'], sqlite_type)
        assert isinstance(_type['impl'], impl_type)