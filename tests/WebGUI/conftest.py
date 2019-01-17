import pytest
import os
import shutil
import tempfile
import json
from experimentum.Experiments import App
from experimentum.WebGUI import create_app


def create_directories_and_files(path):
    """Create dirs and files for the app."""
    def write_file(name, content):
        with open(os.path.join(path, name), 'w+') as fh:
            fh.write(content)

    os.mkdir(os.path.join(path, 'logs'))
    os.mkdir(os.path.join(path, 'experiments'))
    os.mkdir(os.path.join(path, 'migrations'))
    os.mkdir(os.path.join(path, 'repositories'))

    with open(os.path.join(path, 'app.json'), 'w') as outfile:
        json.dump({"prog": "main.py", "description": "Testing."}, outfile)

    with open(os.path.join(path, 'storage.json'), 'w') as outfile:
        json.dump({"datastore": {'drivername': 'sqlite', 'database': 'testing.db'}}, outfile)

    write_file(
        'experiments/TestExperiment.py',
        'from experimentum.Experiments import Experiment\n'
        'class TestExperiment(Experiment):\n'
        '   def run(self): pass\n'
        '   def reset(self): pass'
    )
    write_file(
        'migrations/20190101000000_create_experiments.py',
        'from experimentum.Storage.Migrations import Migration\n'
        'class CreateExperiments(Migration):\n'
        '   revision="20180831134223"\n'
        '   def up(self): pass\n'
        '   def down(self): pass\n'
    )



@pytest.fixture
def app(mocker):
    """Create and configure a new app instance for each test."""

    # create a temporary application directory to isolate the app for each test
    class TestContainer(App):
        config_path = tempfile.mkdtemp()

    create_directories_and_files(TestContainer.config_path)
    container = TestContainer('testing', TestContainer.config_path + '/.')
    container.repositories = {'ExperimentRepository': mocker.MagicMock()}

    # create the app with common test config and set template folder (otherwise it will not be found in testing)
    app = create_app(container, {'TESTING': True })
    app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../experimentum/WebGUI/templates/'))

    yield app

    # remove the temporary app
    shutil.rmtree(TestContainer.config_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
