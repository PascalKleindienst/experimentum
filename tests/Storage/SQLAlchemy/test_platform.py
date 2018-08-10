from experimentum.Storage.SQLAlchemy import Platform
from sqlalchemy import Column, Text, ForeignKey, create_engine


class TestPlatform(object):
    @classmethod
    def setup_class(cls):
        """ init platform """
        cls.platform = Platform()
        cls.engine = create_engine('sqlite://')

    def _setup_platform(self, mocker):
        self.platform.set_engine(
            self.engine,
            mocker.patch('sqlalchemy.schema.MetaData')
        )

    def test_set_engine(self):
        assert self.platform.engine is None
        assert self.platform.meta is None
        self.platform.set_engine('engine', 'meta')
        assert self.platform.engine is 'engine'
        assert self.platform.meta is 'meta'

    def test_get_add_column_sql(self, mocker):
        self._setup_platform(mocker)
        sql = self.platform.get_add_column_sql('foo_table', Column('bar_col', Text))
        assert sql == 'ALTER TABLE foo_table ADD COLUMN bar_col TEXT;'

    def test_get_key_sql_with_foreign_key_with_actions(self, mocker):
        self._setup_platform(mocker)
        col = Column('foreign', Text, ForeignKey('foo.bar', name='foo_bar', ondelete='cascade', onupdate='cascade'))
        sql = self.platform.get_key_sql('baz', col)
        assert sql == [
            'ALTER TABLE baz ADD CONSTRAINT foo_bar '
            'FOREIGN KEY (foreign) REFERENCES foo(bar) '
            'ON DELETE cascade ON UPDATE cascade;'
        ]

    def test_get_key_sql_with_foreign_key_without_actions(self, mocker):
        self._setup_platform(mocker)
        col = Column('foreign', Text, ForeignKey('foo.bar', name='foo_bar'))
        sql = self.platform.get_key_sql('baz', col)
        assert sql == [
            'ALTER TABLE baz ADD CONSTRAINT foo_bar '
            'FOREIGN KEY (foreign) REFERENCES foo(bar)  ;'
        ]

    def test_get_key_sql_without_foreign_key(self, mocker):
        self._setup_platform(mocker)
        col = Column('foreign', Text)
        sql = self.platform.get_key_sql('baz', col)
        assert sql == []

    def test_get_key_sql_with_primary_key(self, mocker):
        self._setup_platform(mocker)
        col = Column('prim', Text, primary_key=True)
        sql = self.platform.get_key_sql('baz', col)
        assert sql == ['ALTER TABLE baz ADD PRIMARY KEY(prim);']

    def test_get_rename_sql(self, mocker):
        self._setup_platform(mocker)
        sql = self.platform.get_rename_sql('foo', 'baz')
        assert sql == 'ALTER TABLE foo RENAME TO baz;'

    def test_get_drop_columns_sql(self, mocker):
        self._setup_platform(mocker)
        sql = self.platform.get_drop_columns_sql('foo', ['bar', 'baz'])
        assert sql == [
            'ALTER TABLE foo DROP COLUMN bar;',
            'ALTER TABLE foo DROP COLUMN baz;'
        ]