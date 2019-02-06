from experimentum.Commands import AbstractCommand, command
import pytest

class TestAbstractCommand(object):
    @classmethod
    def setup_class(cls):
        """ setup abstract command """
        cls.cmd = AbstractCommand()

    def test_setup_method(self):
        self.cmd.setup('Some Desc', {'foo': 'bar'}, 'some help')
        assert self.cmd.description is 'Some Desc'
        assert self.cmd.arguments == {'foo': 'bar'}
        assert self.cmd.help is 'some help'

    def test_abstract_handle_method(self):
        with pytest.raises(NotImplementedError):
            self.cmd.handle(None, {})

    def test_command_decorator(self):
        @command('Mock Desc', {'foo': 1}, 'help')
        def mock_command():
            return True

        cmd = mock_command()
        assert isinstance(cmd, AbstractCommand)
        assert cmd.description is 'Mock Desc'
        assert cmd.arguments == {'foo': 1}
        assert cmd.help is 'help'
        assert cmd.handle() is True
