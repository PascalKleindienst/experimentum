from experimentum.Experiments import App, app as _app
from experimentum.Config import Config
from experimentum.Commands import CommandManager
import logging
import pytest

class TestApp(object):
    def test_set_name(self):
        app = App('Foo App')
        assert 'Foo App' == app.name

    def test_boostrapping_app(self):
        app = App('')
        assert isinstance(app.config, Config)
        assert isinstance(app.log, logging.Logger)
        assert isinstance(app.cmd_manager, CommandManager)
        assert app is _app()

    def test_adding_user_commands(self, mocker):
        cmd_manager = mocker.patch('experimentum.Commands.CommandManager')
        cmd_manager.add_command = mocker.MagicMock()

        user_cmd = {'foo': lambda: mocker.patch('experimentum.Commands.AbstractCommand') }

        app = App('')
        app.cmd_manager = cmd_manager
        app.register_commands = lambda: user_cmd
        app._add_commands()

        cmd_manager.add_command.assert_any_call('foo', user_cmd['foo'])

    def test_dispatching_commands_on_run(self, mocker):
        cmd_manager = mocker.patch('experimentum.Commands.CommandManager')
        cmd_manager.dispatch = mocker.MagicMock()

        app = App('')
        app.cmd_manager = cmd_manager
        app.run()

        cmd_manager.dispatch.assert_called_once()

    def test_make_alias_instance(self, mocker):
        app = App('')
        app.aliases = {'foo': lambda: mocker.MagicMock() }
        assert isinstance(app.make('foo'), mocker.MagicMock)

    def test_make_invalid_alias_instance(self):
        app = App('')
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            app.make('foo')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1