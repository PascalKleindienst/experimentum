from experimentum.Storage.SQLAlchemy import Platform
from sqlalchemy import Column, Text, ForeignKey, create_engine


class TestPlatform(object):
    @classmethod
    def setup_class(cls):
        """ init platform """
        cls.engine = create_engine('sqlite://')

    def _setup_platform(self, mocker):
        self.platform = Platform()
        self.platform.set_engine(
            self.engine,
            mocker.patch('sqlalchemy.schema.MetaData')
        )

    def test_set_engine(self):
        platform = Platform()
        assert platform.engine is None
        assert platform.meta is None
        platform.set_engine('engine', 'meta')
        assert platform.engine is 'engine'
        assert platform.meta is 'meta'

    def test_is_sqlite(self, mocker):
        self._setup_platform(mocker)
        dialect = self.platform.engine.dialect
        self.platform.engine.dialect = mocker.patch('sqlalchemy.dialects.sqlite.base.SQLiteDialect', spec=True)
        assert self.platform.is_sqlite() is True
        self.platform.engine.dialect = dialect

    def test_is_mysql(self, mocker):
        self._setup_platform(mocker)
        dialect = self.platform.engine.dialect
        self.platform.engine.dialect = mocker.patch('sqlalchemy.dialects.mysql.base.MySQLDialect', spec=True)
        assert self.platform.is_mysql() is True
        self.platform.engine.dialect = dialect

    def test_is_mssql(self, mocker):
        self._setup_platform(mocker)
        dialect = self.platform.engine.dialect
        self.platform.engine.dialect = mocker.patch('sqlalchemy.dialects.mssql.base.MSDialect', spec=True)
        assert self.platform.is_mssql() is True
        self.platform.engine.dialect = dialect

    def test_get_add_column_sql(self, mocker):
        self._setup_platform(mocker)
        sql = self.platform.get_add_column_sql('foo_table', Column('bar_col', Text))
        assert sql == 'ALTER TABLE foo_table ADD COLUMN bar_col TEXT;'

    def test_get_key_sql_with_foreign_key_with_actions(self, mocker):
        assert self._get_key(mocker, ForeignKey('foo.bar', name='foo_bar', ondelete='cascade', onupdate='cascade')) == [
            'ALTER TABLE baz ADD CONSTRAINT foo_bar '
            'FOREIGN KEY (foobar) REFERENCES foo(bar) '
            'ON DELETE cascade ON UPDATE cascade;'
        ]

    def test_get_key_sql_with_foreign_key_without_actions(self, mocker):
        assert self._get_key(mocker, ForeignKey('foo.bar', name='foo_bar')) == [
            'ALTER TABLE baz ADD CONSTRAINT foo_bar '
            'FOREIGN KEY (foobar) REFERENCES foo(bar)  ;'
        ]

    def test_get_key_sql_without_foreign_key(self, mocker):
        assert self._get_key(mocker) == []

    def test_get_key_sql_with_primary_key(self, mocker):
        assert self._get_key(mocker, primary_key=True) == ['ALTER TABLE baz ADD PRIMARY KEY(foobar);']

    def test_get_rename_sql(self, mocker):
        self._setup_platform(mocker)
        assert self.platform.get_rename_sql('foo', 'baz') == 'ALTER TABLE foo RENAME TO baz;'

    def test_get_drop_columns_sql(self, mocker):
        self._setup_platform(mocker)
        assert self.platform.get_drop_columns_sql('foo', ['bar', 'baz']) == [
            'ALTER TABLE foo DROP COLUMN bar;',
            'ALTER TABLE foo DROP COLUMN baz;'
        ]

    def test_get_drop_key_constraint_sql_drop_primary(self, mocker):
        assert self._drop_key(mocker, 'primary') == 'ALTER TABLE foo DROP CONSTRAINT foo_bar_primary;'
        assert self._drop_key(mocker, 'primary', 'is_mysql') == 'ALTER TABLE foo CHANGE baz baz TEXT UNSIGNED NOT NULL; ' \
            'ALTER TABLE foo DROP PRIMARY KEY;'

    def test_get_drop_key_constraint_sql_drop_unique(self, mocker):
        assert self._drop_key(mocker, 'unique') == 'ALTER TABLE foo DROP CONSTRAINT foo_bar_unique;'
        assert self._drop_key(mocker, 'unique', 'is_mysql') == 'ALTER TABLE foo DROP INDEX foo_bar_unique;'

    def test_get_drop_key_constraint_sql_drop_foreign(self, mocker):
        assert self._drop_key(mocker, 'foreign') == 'ALTER TABLE foo DROP CONSTRAINT foo_bar_foreign;'
        assert self._drop_key(mocker, 'foreign', 'is_mysql') == 'ALTER TABLE foo DROP FOREIGN KEY foo_bar_foreign;'

    def test_get_drop_key_constraint_sql_drop_index(self, mocker):
        assert self._drop_key(mocker, 'index') == 'DROP INDEX foo_bar_index;'
        assert self._drop_key(mocker, 'index', 'is_mysql') == 'ALTER TABLE foo DROP INDEX foo_bar_index;'
        assert self._drop_key(mocker, 'index', 'is_mssql') == 'DROP INDEX foo_bar_index ON foo;'

    def _get_key(self, mocker, *args, **kwargs):
        self._setup_platform(mocker)
        col = Column('foobar', Text, *args, **kwargs)
        return self.platform.get_key_sql('baz', col)

    def _drop_key(self, mocker, idx, dialect=None):
        self._setup_platform(mocker)
        self.platform.__dict__[dialect] = mocker.MagicMock(return_value=True)
        col = Column('baz', Text)

        if dialect:
            setattr(self.platform, dialect, mocker.MagicMock(return_value=True))

        return self.platform.get_drop_key_constraint_sql('foo', col, idx, 'foo_bar_' + idx)