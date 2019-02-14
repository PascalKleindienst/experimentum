from experimentum.Storage import AbstractStore
from experimentum.Experiments import App
import tempfile
import pytest


class CustomStore(AbstractStore):

    """Custom AbstractStore implementation."""

    def has_table(self, table):
        pass

    def has_column(self, table, column):
        pass

    def create(self, blueprint):
        pass

    def rename(self, old, new):
        pass

    def drop(self, name, checkfirst=False):
        pass

    def alter(self, blueprint):
        pass


class TestStore():
    def test_crud_operations(self, cli_app):
        """
        GIVEN the framework is installed and the standard tables have some entries
        WHEN a user uses the TestRepository to create, read, update, delete entries
        THEN these operations are executed on the database
        """
        # User access the testcase repository
        cli_app.store.session.execute(
            'INSERT INTO experiments(id, name, start) VALUES(1, "foo", "1970-01-01 00:00:00");'
        )
        repo = cli_app.repositories.get('TestCaseRepository')

        # User create a new entry in the testcase table
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 0
        new_test = repo(iteration=1337, experiment_id=1)
        new_test.create()
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 1

        # # User reads previously added entry
        entry = repo.find(1)
        assert entry.iteration == 1337
        assert entry.experiment_id == 1

        # Update previously fetched entry
        entry.iteration = 21
        entry.update()
        assert cli_app.store.session.execute('SELECT iteration FROM testcases;').first()[0] == 21

        # Delete entry from database
        entry.delete()
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 0

    def test_custom_store(self, app_files):
        """
        GIVEN the framework is installed and the standard tables exist
        WHEN the user creates a custom AbstractStore implementation
        THEN the framework will use the implementation without problem
        """
        # User sets up the custom data store and the test app
        my_store = CustomStore()

        class TestContainer(App):
            config_path = tempfile.mkdtemp()

            def setup_datastore(self, datastore):
                self.store = my_store

        # User initialises the application
        app_files.create_directories_and_files(TestContainer.config_path)
        container = TestContainer('testing', TestContainer.config_path + '/.')

        # The application store should be the custom store implementation
        assert container.store == my_store
        assert isinstance(container.store, CustomStore)
        assert isinstance(container.make('store'), CustomStore)

    def test_invalid_store(self, capsys, app_files):
        """
        GIVEN the framework is installed and the standard tables exist
        WHEN the user uses a custom invalid store implementation
        THEN the framework will throw an error
        """
        # User sets up the custom data store and the test app
        class InvalidStore(object):
            pass

        class TestContainer(App):
            config_path = tempfile.mkdtemp()

            def setup_datastore(self, datastore):
                self.store = InvalidStore()

        # User initialises the application
        app_files.create_directories_and_files(TestContainer.config_path)
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            TestContainer('testing', TestContainer.config_path + '/.')

        # The application should abort and print an error message
        assert 'Store implementation must implement the AbstractStore' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
