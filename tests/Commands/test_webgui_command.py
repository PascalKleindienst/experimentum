import argparse
from experimentum.Commands.WebGUICommand import start
import werkzeug.serving


class TestWebGUICommand(object):
    def setup_mocks(self, mocker):
        server_mock = mocker.patch('experimentum.WebGUI.Server')
        server_mock.start = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=server_mock)

        return server_mock, app_mock

    def test_start_default(self, mocker):
        server_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(port=5000)

        start().handle(app_mock, args)

        server_mock.run.assert_called_once_with( 5000, False, True)

    def test_start_with_debugger_and_no_reload(self, mocker):
        server_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(port=8080, debug=True, reload=False)

        start().handle(app_mock, args)

        server_mock.run.assert_called_once_with(8080, True, False)

