from experimentum.Storage.SQLAlchemy import SQLitePlatform
from sqlalchemy import Column, Text, Table, create_engine, MetaData
from sqlalchemy import inspect, ForeignKey, Index

class TestSQLitePlatform(object):
    @classmethod
    def setup_class(cls):
        """ init platform """
        cls.platform = SQLitePlatform()
        cls.engine = create_engine('sqlite://')
        cls.meta = MetaData(cls.engine)

    def _setup_platform(self):
        self.platform.set_engine(
            self.engine,
            self.meta
        )

    def test_set_engine(self):
        assert self.platform.engine is None
        assert self.platform.meta is None
        self.platform.set_engine('engine', 'meta')
        assert self.platform.engine is 'engine'
        assert self.platform.meta is 'meta'

    def test_if_is_sqlite_dialect(self):
        self._setup_platform()
        assert self.platform.is_sqlite_dialect() is True

    def test_alter_table_add_column(self):
        inspector = inspect(self.platform.engine)
        table = Table('foo', self.platform.meta, Column('bar', Text), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [Column('baz', Text)], [])
        assert len(inspector.get_columns('foo')) == 2

    def test_alter_table_with_old_foreign_key(self):
        inspector = inspect(self.platform.engine)
        table = Table('foobar', self.platform.meta, Column('bar', Text), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        fkey = ForeignKey('foobar.bar')
        table = Table('foo', self.platform.meta, Column('bar', Text, fkey), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [Column('baz', Text)], [])
        assert table.foreign_keys == set([fkey])
