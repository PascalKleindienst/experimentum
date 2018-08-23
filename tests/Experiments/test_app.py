from experimentum.Experiments import App
from experimentum.Config import Config
from experimentum.Commands import CommandManager
import json
import os
import logging
import pytest

class TestApp(object):

    def setup_app(self, name, root):
        """ setup """
        with open(os.path.join(root, 'app.json'), 'w+') as outfile:
            json.dump({
                "prog": "test.py",
                "description": "Test",
                "logging": {"level": "DEBUG"}
            }, outfile)

        return App(name, os.path.join(root, 'main.py'))

    def test_set_name(self, tmpdir):
        app = self.setup_app('Foo App', tmpdir.strpath)
        assert 'Foo App' == app.name

    def test_boostrapping_app(self, tmpdir):
        app = self.setup_app('', tmpdir.strpath)
        assert isinstance(app.config, Config)
        assert isinstance(app.log, logging.Logger)
        assert isinstance(app.cmd_manager, CommandManager)

    def test_adding_user_commands(self, mocker, tmpdir):
        cmd_manager = mocker.patch('experimentum.Commands.CommandManager')
        cmd_manager.add_command = mocker.MagicMock()

        user_cmd = {'foo': lambda: mocker.patch('experimentum.Commands.AbstractCommand') }

        app = self.setup_app('', tmpdir.strpath)
        app.cmd_manager = cmd_manager
        app.register_commands = lambda: user_cmd
        app._add_commands()

        cmd_manager.add_command.assert_any_call('foo', user_cmd['foo'])

    def test_dispatching_commands_on_run(self, mocker, tmpdir):
        cmd_manager = mocker.patch('experimentum.Commands.CommandManager')
        cmd_manager.dispatch = mocker.MagicMock()

        app = self.setup_app('', tmpdir.strpath)
        app.cmd_manager = cmd_manager
        app.run()

        cmd_manager.dispatch.assert_called_once_with()

    def test_make_alias_instance(self, mocker, tmpdir):
        app = self.setup_app('', tmpdir.strpath)
        app.aliases = {'foo': lambda: mocker.MagicMock() }
        assert isinstance(app.make('foo'), mocker.MagicMock)

    def test_make_invalid_alias_instance(self, tmpdir):
        app = self.setup_app('', tmpdir.strpath)
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            app.make('foo')
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1