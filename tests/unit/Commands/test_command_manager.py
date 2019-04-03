from experimentum.Commands import CommandManager, command
import pytest
import argparse
import sys
from termcolor import colored

class TestCommandManager(object):
    def test_init(self, mocker):
        manager = CommandManager(mocker.patch('experimentum.Experiments.App'), 'Test Prog', 'Test Desc')
        assert isinstance(manager._parser, argparse.ArgumentParser)
        assert isinstance(manager._subparsers, argparse._SubParsersAction)

    def test_add_invalid_command(self, mocker):
        manager = CommandManager(mocker.patch('experimentum.Experiments.App'), 'Test Prog', 'Test Desc')
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            manager.add_command('foo', TestCommandManager)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_add_command(self, mocker):
        manager = CommandManager(mocker.patch('experimentum.Experiments.App'), 'Test Prog', 'Test Desc')
        @command(
            description='Foo Command',
            help='Some help text',
            arguments={
                '--bar': {'action': 'store_true', 'help': 'Bar Help'}
            }
        )
        def foo_command(args):
            pass

        manager.add_command('foo', foo_command)

        cmd = manager.commands['foo']
        assert isinstance(cmd, argparse.ArgumentParser)
        assert cmd.description == colored('Foo Command', 'yellow')

    def test_dispatch_with_invalid_args(self, mocker):
        manager = CommandManager(mocker.patch('experimentum.Experiments.App'), 'Test Prog', 'Test Desc')
        sys.argv = ["prog", "foo", '-b']
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            manager.dispatch()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_dispatch(self, mocker):
        mock_app = mocker.patch('experimentum.Experiments.App')
        manager = CommandManager(mock_app, 'Test Prog', 'Test Desc')
        sys.argv = ["prog", "foobar", '42']
        @command(help='Help me', arguments={'bar': {'default': 1337, 'nargs': '?'}})
        def foobar(app, args):
            assert app is mock_app
            assert args.bar == '42'

        manager.add_command('foobar', foobar)
        manager.dispatch()

    def test_dispatch_without_args(self, mocker):
        mock_app = mocker.patch('experimentum.Experiments.App')
        manager = CommandManager(mock_app, 'Test Prog', 'Test Desc')
        sys.argv = ["prog", "foobar"]
        @command(help='Help me')
        def foobar(app, args=None):
            assert app is mock_app
            assert args is None

        manager.add_command('foobar', foobar)
        manager.dispatch()
