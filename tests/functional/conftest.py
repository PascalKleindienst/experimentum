"""PyTest fixtures"""
import pytest
import tempfile
import os
import json
from experimentum.Experiments import App
from shutil import copyfile, rmtree
from sqlalchemy.orm import clear_mappers


class AppFileHandler(object):
    def create_directories_and_files(self, path):
        """Create dirs and files for the app.

        Args:
            path (str): Root Path
        """
        # Create Folders
        folders = ['logs', 'experiments', 'migrations', 'repositories']
        for folder in folders:
            os.mkdir(os.path.join(path, folder))

        # Create Init files
        with open(os.path.join(path, 'repositories', '__init__.py'), 'w+') as outfile:
            outfile.write('')

        # Create Config Files
        cfg = {
            'app.json': {'prog': 'main.py', 'description': 'Testing.'},
            'storage.json': {
                'datastore': {'drivername': 'sqlite', 'database': 'test.db'},
                'migrations': {'path': 'migrations'}
            }
        }
        for key, item in cfg.items():
            with open(os.path.join(path, key), 'w') as outfile:
                json.dump(item, outfile)

        # Create Stubs
        stubs = [
            {'name': '20190101000000_create_experiments', 'target': 'migrations/{name}.py'},
            {'name': '20190101000001_create_testcase', 'target': 'migrations/{name}.py'},
            {'name': '20190101000002_create_performance', 'target': 'migrations/{name}.py'},
            {'name': 'ExperimentRepository', 'target': 'repositories/{name}.py'},
            {'name': 'TestCaseRepository', 'target': 'repositories/{name}.py'},
            {'name': 'PerformanceRepository', 'target': 'repositories/{name}.py'},
        ]
        for stub in stubs:
            self.create_from_stub(path, stub['name'], stub['target'])

    def create_from_stub(self, path, name, target):
        """Create a file from a stub file.

        Args:
            path (str): Path where new file is stored
            name (str): name of the stub
            target (str): filepath of the new file
        """
        root = os.path.dirname(os.path.realpath(__file__))

        copyfile(
            os.path.join(root, '_stubs', '{}.stub'.format(name)),
            os.path.join(path, target.replace('{name}', name))
        )


@pytest.fixture
def app_files():
    """Helper for handling file related issues."""
    filehandler = AppFileHandler()
    yield filehandler


@pytest.fixture(scope='function')
def cli_app(app_files):
    """Create the cli app."""
    # create a temporary application directory to isolate the app for each test
    class TestContainer(App):
        config_path = tempfile.mkdtemp()

    app_files.create_directories_and_files(TestContainer.config_path)
    container = TestContainer('testing', TestContainer.config_path + '/.')

    # Init Database & clear previously mapped repos, otherwise there are some error with the mapping
    migrator = container.make('migrator')
    migrator.refresh()
    clear_mappers()
    container.bootstrap()

    yield container

    # Delete App and Files/Folders
    container.store.session.close_all()
    container.store.engine.dispose()
    handlers = container.log.handlers[:]
    for handler in handlers:
        handler.close()
        container.log.removeHandler(handler)
    rmtree(TestContainer.config_path)
