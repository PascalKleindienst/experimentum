from experimentum.Storage.SQLAlchemy import SQLitePlatform
from sqlalchemy import Column, Text, Table, create_engine, MetaData
from sqlalchemy import inspect, ForeignKey, Index


class TestSQLitePlatform(object):
    @classmethod
    def setup_class(cls):
        """ init platform """
        cls.platform = SQLitePlatform()

    def _setup_platform(self):
        engine = create_engine('sqlite://')
        self.platform.set_engine(
            engine,
            MetaData(engine)
        )

    def test_set_engine(self):
        assert self.platform.engine is None
        assert self.platform.meta is None
        self.platform.set_engine('engine', 'meta')
        assert self.platform.engine is 'engine'
        assert self.platform.meta is 'meta'

    def test_alter_table_add_column(self):
        self._setup_platform()
        inspector = inspect(self.platform.engine)
        table = Table('foo', self.platform.meta, Column('bar', Text), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [Column('baz', Text)], {'columns': [], 'indexes': []})
        assert len(inspector.get_columns('foo')) == 2

    def test_alter_table_with_old_foreign_key(self):
        self._setup_platform()
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
        self.platform.alter_table('foo', [Column('baz', Text)], {'columns': [], 'indexes': []})
        assert table.foreign_keys == set([fkey])

    def test_alter_table_add_unique_index(self):
        self._setup_platform()
        inspector = inspect(self.platform.engine)
        columns = [Column('bar', Text)]
        table = Table('foo', self.platform.meta, *columns, extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1
        assert len(table.indexes) == 0

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [Index('foo_bar_unique', *columns, unique=True)], {'columns': [], 'indexes': []})
        assert len(table.indexes) == 1
        assert list(table.indexes)[0].unique == 1

    def test_alter_table_drop_primary(self):
        self._setup_platform()
        inspector = inspect(self.platform.engine)
        table = Table('foo', self.platform.meta, Column('bar', Text, primary_key=True), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1
        assert inspector.get_pk_constraint('foo')['constrained_columns'] == ['bar']

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [], {'columns': [], 'indexes': [{'type': 'primary', 'col': 'bar', 'name': 'foo_bar_primary'}]})
        assert inspector.get_pk_constraint('foo')['constrained_columns'] == []

    def test_alter_table_drop_index(self):
        self._setup_platform()
        inspector = inspect(self.platform.engine)
        column = Column('bar', Text)
        table = Table('foo', self.platform.meta, column, Index('foo_bar_index', column), extend_existing=True)
        table.drop(self.platform.engine, checkfirst=True)
        table.create(self.platform.engine)

        assert 'foo' in inspector.get_table_names()
        assert table.columns.keys() == ['bar']
        assert len(inspector.get_columns('foo')) == 1
        assert inspector.get_indexes('foo')[0].get('name') == 'foo_bar_index'
        assert inspector.get_indexes('foo')[0].get('unique') == 0

        inspector = inspect(self.platform.engine)
        self.platform.alter_table('foo', [], {'columns': [], 'indexes': [{'type': 'index', 'col': 'bar', 'name': 'foo_bar_index'}]})
        assert inspector.get_indexes('foo') == []
