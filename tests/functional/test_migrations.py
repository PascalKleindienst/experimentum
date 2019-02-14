import sys
import os
import glob
from shutil import copy
from experimentum.WebGUI.helpers import ansi_escape
from sqlalchemy.engine import reflection
from sqlalchemy.types import INTEGER, VARCHAR


def _create_migration(app):
    """Create a new migration.

    Args:
        app (App): Service Container
    """
    root = os.path.dirname(os.path.realpath(__file__))
    copy(
        os.path.join(root, '_stubs/20190101000002_create_custom.stub'),
        os.path.join(
            app.root, app.config.get('storage.migrations.path'),
            '20190101000002_create_custom.py'
        )
    )


class TestMigration(object):
    def test_migration_up(self, cli_app, capsys):
        """
        GIVEN the framework is installed and the experiments and testcases tables exist
        WHEN a user executes a new migration
        THEN the database schema should be modified accordingly
        """
        # User creates a new migration
        _create_migration(cli_app)

        # User executes the migration
        sys.argv = ['main.py', 'migration:up']
        cli_app.run()

        # New migration should be executed
        assert 'Migrated 20190101000002_create_custom' in ansi_escape(capsys.readouterr().out)

        # Database schema should be changed
        insp = reflection.Inspector.from_engine(cli_app.store.engine)
        assert 'foo' in cli_app.store.engine.table_names()
        assert insp.get_columns('testcases')[3]['name'] == 'bar'
        assert isinstance(insp.get_columns('testcases')[3]['type'], INTEGER)
        assert insp.get_columns('foo')[0]['name'] == 'id'
        assert isinstance(insp.get_columns('foo')[0]['type'], INTEGER)
        assert insp.get_columns('foo')[1]['name'] == 'name'
        assert isinstance(insp.get_columns('foo')[1]['type'], VARCHAR)

    def test_migration_down(self, cli_app, capsys):
        """
        GIVEN the framework is installed and the experiments and testcases tables exist
        WHEN a user reverts to an old migration
        THEN the database schema should be modified accordingly
        """
        # User reverts the test migration
        sys.argv = ['main.py', 'migration:down']
        cli_app.run()

        # migration should be reverted
        assert 'Migrated 20190101000001_create_testcase' in ansi_escape(capsys.readouterr().out)

        # Database schema should be changed
        assert ['experiments'] == cli_app.store.engine.table_names()

    def test_migration_status(self, cli_app, capsys):
        """
        GIVEN the framework is installed
        WHEN a user wants to get the status of all migrations
        THEN the migration status should be displayed
        """
        # Not executed migration
        _create_migration(cli_app)

        # User gets the migration status
        sys.argv = ['main.py', 'migration:status']
        cli_app.run()

        # display migration status
        output = ansi_escape(capsys.readouterr().out)
        assert '20190101000000_create_experiments | Yes' in output
        assert '20190101000001_create_testcase    | Yes' in output
        assert '20190101000002_create_custom      | No' in output

    def test_migration_refresh(self, cli_app):
        """
        GIVEN the framework is installed
        WHEN a user wants to get the status of all migrations
        THEN the migration status should be displayed
        """
        # Fill Database
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 0
        cli_app.store.session.execute(
            'INSERT INTO testcases (iteration, experiment_id) VALUES (1, 1);'
        )
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 1
        cli_app.store.session.close()

        # User refreshes database
        sys.argv = ['main.py', 'migration:refresh']
        cli_app.run()

        # database should be empty
        assert 'experiments' in cli_app.store.engine.table_names()
        assert 'testcases' in cli_app.store.engine.table_names()
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 0

    def test_migration_make(self, cli_app, capsys):
        """
        GIVEN the framework is installed
        WHEN a user wants create a new migration
        THEN the migration stub should be created
        """
        # Check that migration does not already exist
        pattern = os.path.join(cli_app.root, cli_app.config.get('storage.migrations.path'), '*.py')
        assert len(glob.glob(pattern)) == 2

        # User refreshes database
        sys.argv = ['main.py', 'migration:make', '"My Migration"']
        cli_app.run()

        # database should be empty
        assert 'Migration created successfully!' in ansi_escape(capsys.readouterr().out)
        assert len(glob.glob(pattern)) == 3
        assert '_my_migration.py' in glob.glob(pattern)[-1]
