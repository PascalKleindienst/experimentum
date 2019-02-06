from experimentum.Storage.Migrations import Schema, Blueprint
import logging
import pytest


class TestSchema(object):
    def _setup(self, mocker):
        """ init platform """
        mock_app = mocker.patch('experimentum.Experiments.App', log=logging, spec=True)
        mock_storage = mocker.patch('experimentum.Storage.SQLAlchemy.Store', spec=True)
        mock_blueprint = mocker.patch('experimentum.Storage.Migrations.Blueprint', spec=True)
        mock_blueprint.create = mocker.MagicMock()
        mock_app.make = lambda x, *args, **kwargs: mock_storage if x == 'store' else mock_blueprint
        self.schema = Schema(mock_app)

    def test_create(self, mocker):
        self._setup(mocker)

        with self.schema.create('Test') as table:
            assert isinstance(table, Blueprint) is True
            table.action = 'create'
            table.create.assert_called_once_with()

        self.schema.store.create.assert_called_once_with(table)

    def test_create_error_while_creating_blueprint(self, mocker):
        self._setup(mocker)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            self.schema.app.make = {}
            self.schema.create('Test').__enter__()

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_table(self, mocker):
        self._setup(mocker)

        with self.schema.table('Test') as table:
            assert isinstance(table, Blueprint) is True
            table.action = 'alter'

        self.schema.store.alter.assert_called_with(table)

    def test_table_error_while_creating_blueprint(self, mocker):
        self._setup(mocker)

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            self.schema.app.make = {}
            self.schema.table('Test').__enter__()

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_rename(self, mocker):
        self._setup(mocker)
        self.schema.rename('foo', 'baz')
        self.schema.store.rename.assert_called_with('foo', 'baz')

    def test_drop(self, mocker):
        self._setup(mocker)
        self.schema.drop('foo')
        self.schema.store.drop.assert_called_with('foo')

    def test_drop_if_exists(self, mocker):
        self._setup(mocker)
        self.schema.drop_if_exists('foo')
        self.schema.store.drop_if_exists.assert_called_with('foo')

    def test_has_table(self, mocker):
        self._setup(mocker)
        self.schema.has_table('foo')
        self.schema.store.has_table.assert_called_with('foo')

    def test_has_column(self, mocker):
        self._setup(mocker)
        self.schema.has_column('foo', 'bar')
        self.schema.store.has_column.assert_called_with('foo', 'bar')
