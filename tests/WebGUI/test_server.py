from experimentum.WebGUI import Server
from flask import Flask


class TestServer(object):
    def test_create_app(self, mocker):
        # Create app
        mock = mocker.patch('experimentum.Experiments.App')
        server = Server(mock)
        app = server.create_app()

        # Assertions
        assert isinstance(app, Flask)
        assert app.config['TEMPLATES_AUTO_RELOAD']
        assert app.config['TESTING'] is False
        assert app.config['container'] == mock

    def test_create_app_for_testing(self, mocker):
        # Create app
        mock = mocker.patch('experimentum.Experiments.App')
        server = Server(mock, testing=True)
        app = server.create_app()

        # Assertions
        assert app.config['TESTING']

    def test_create_app_custom_config(self, mocker):
        # Create app
        mock = mocker.patch('experimentum.Experiments.App')
        mock.config.get.return_value = {'foo': 'bar', 'TEMPLATES_AUTO_RELOAD': False}
        server = Server(mock)
        app = server.create_app()

        # Assertions
        assert app.config['TEMPLATES_AUTO_RELOAD'] is False
        assert app.config['foo'] == 'bar'