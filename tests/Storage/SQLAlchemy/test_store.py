from experimentum.Storage.SQLAlchemy import Store
from experimentum.Storage.Migrations import Blueprint
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, inspect
from sqlalchemy.orm.session import Session
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
        assert isinstance(store.session, Session)

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
        assert 'fkey_name' == inspector.get_foreign_keys('foo')[0]['name']
        assert {'unique': 0, 'name': u'foo_some_key_index', 'column_names': [u'some_key']} in inspector.get_indexes('foo')
        assert {'unique': 1, 'name': u'foo_unique_key_unique', 'column_names': [u'unique_key']} in inspector.get_indexes('foo')
