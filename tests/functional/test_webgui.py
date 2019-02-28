import sys
import os
import re
import pytest
import glob
import time


def start_server():
    import tempfile
    from conftest import AppFileHandler
    from experimentum.Experiments import App
    from experimentum.WebGUI import Server

    # App Container
    class WebAppContainer(App):
        config_path = tempfile.mkdtemp()

    # Test Server
    class TestServer(Server):
        def create_app(self):
            app = super(TestServer, self).create_app()
            app.template_folder = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                '../../experimentum/WebGUI/templates/'
            ))

            return app

    # Setup args
    main = os.path.join(WebAppContainer.config_path, 'main.py')
    sys.argv = [main, 'webgui', '--port', '3000', '--no-reload']

    # add files and dirs
    app_files = AppFileHandler()
    app_files.create_directories_and_files(WebAppContainer.config_path)

    # init container and testserver and run command
    container = WebAppContainer('testing', WebAppContainer.config_path + '/.')
    container.aliases['server'] = lambda: TestServer(container, True)
    container.run()


class TestWebGUI():
    def test_webui_available(self, app_files):
        """
        GIVEN the framework is installed
        WHEN a user starts the webgui on port 3000
        THEN the gui is available on localhost:3000
        """
        from multiprocessing import Process
        from six.moves import urllib

        # check that webgui is not available yet
        with pytest.raises(urllib.error.URLError) as pytest_wrapped_e:
            urllib.request.urlopen('http://localhost:3000')
        assert pytest_wrapped_e.type == urllib.error.URLError

        # User starts the webgui on port 3000
        web_gui = Process(target=start_server)
        web_gui.start()

        # webgui should be available after some startup time
        time.sleep(30.0)
        assert urllib.request.urlopen('http://localhost:3000').getcode() == 200

        # Stop webgui process
        web_gui.terminate()
        web_gui.join()
        del(web_gui)

    def test_manage_migrations(self, webclient):
        """
        GIVEN the framework is installed and the webgui is accessable
        WHEN the user creates, upgrades, and downgrades a migration
        THEN these actions are executed on the migration
        """
        # User creates a new migration foo
        webclient.post('/migrations/make', data={'name': 'create foo migration'})
        response = webclient.get('/')
        root = webclient.application.config['container'].root

        assert len(glob.glob(os.path.join(root, 'migrations', '*_create_foo_migration.py'))) == 1
        assert re.search(
            '<i class="material-icons">error<\\/i>\\s*\\d{14}_create_foo_migration',
            response.get_data(as_text=True),
            re.MULTILINE | re.IGNORECASE
        )

        # User upgrades to new migration
        webclient.get('/migrations/upgrade')
        response = webclient.get('/')
        assert re.search(
            '<i class="material-icons">check_circle<\\/i>\\s*\\d{14}_create_foo_migration',
            response.get_data(as_text=True),
            re.MULTILINE | re.IGNORECASE
        )

        # User downgrades migration
        webclient.get('/migrations/downgrade')
        response = webclient.get('/')
        assert re.search(
            '<i class="material-icons">error<\\/i>\\s*\\d{14}_create_foo_migration',
            response.get_data(as_text=True),
            re.MULTILINE | re.IGNORECASE
        )

    def test_manage_experiments(self, webclient, app_files):
        """
        GIVEN the framework is installed, the webgui is accessable, and there
            is an Experiment called FooExperiment with an associated FooPlot class
        WHEN the user executes the experiment with 2 iterations
        THEN the experiment is executed 2 times and a diagramm is generated, and the
            user sees the output log and performance table
        """
        # Create FooExperiment (FooPlot class already exists)
        app_files.create_from_stub(
            webclient.application.config['container'].root,
            'FooExperiment',
            'experiments/{name}.py'
        )
        response = webclient.get('/')
        assert 'Foo' in response.get_data(as_text=True)

        # User submits experiment run form with iterations=2
        response = webclient.post('/experiments/run/foo', data={'iterations': 2, 'config': ''})

        # User sees the experiment result
        data = response.get_data(as_text=True)
        assert '<div id="result" class="col s12"></div>' in data
        assert '<div id="plots" class="col s12">' in data
        assert 'Running Tests' in data
        assert 'Generating Plots' in data
        assert "log_stream('/experiments/run/foo?config=&iterations=2'" in data
