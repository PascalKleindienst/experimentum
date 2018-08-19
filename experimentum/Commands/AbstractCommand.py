"""Easily add CLI commands to the app.

There are to possible ways for defining CLI commands in
order for them to be added to the :py:mod:`.CommandManager`.

Decorator
---------
The easiest method to define a command is via the :py:func:`.AbstractCommand.command`
decorator. The decorator accepts some arguments like description or help text in order
to descrine the command while the decorated function handles the command execution.
The ``arguments`` argument accepts a dictionary which each key is the name of the argument
and each value is passed to the :py:func:`argparse.add_argument` method::

    @command(
        'Some description about what the command does.',
        arguments={
            'integers': {'help': 'Some Help', 'default': 42, 'nargs': '?'},
            '--bar': {'action': 'store_true', 'help': 'Bar Help'}
        }
        help='Short help text.'
    )
    def foo(app, args):
        print(args)


Class-based
-----------
The other way of defining a command is a class based approach. Your command class
has to derived from the :py:class:`.AbstractCommand` class. Just like the decorator
you can define description, arguments and a help text. The ``handle`` method handles
the command execution::

    class FooCommand(AbstractCommand):
        description = 'Some description about what the command does'
        arguments = {
            'integers': {'help': 'Some Help', 'default': 42, 'nargs': '?'},
            '--bar': {'action': 'store_true', 'help': 'Bar Help'}
        }
        help='Short help text.'

        def handle(self, app, args):
            print(args)
"""


def command(description='', arguments={}, help=''):
    """Command decorator, creates a Command to use with the CommandManager.

    Args:
        description (str, optional): Defaults to ''. Description of the command.
        arguments (dict, optional): Defaults to {}. Arguments for the command.
        help (str, optional): Defaults to ''. Help text of the command.

    Returns:
        function:
    """
    def command_decorator(command):
        def command_wrapper(args=None):
            cmd = AbstractCommand()
            cmd.setup(description, arguments, help)
            cmd.handle = command
            return cmd
        return command_wrapper
    return command_decorator


class AbstractCommand(object):

    """Abstract Command Class.

    Attributes:
        description (str): Description of the command.
        arguments (dict): Optional aguments for the command.
        help (str): Help Text for the command.
        args (dict): Dictionary with possible passed arguments.
    """
    description = ''
    help = ''
    arguments = {}
    args = {}

    def setup(self, description='', arguments={}, help=''):
        """Set up the command.

        Args:
            description (str, optional): Defaults to ''. Description of the command.
            arguments (dict, optional): Defaults to {}. Optional aguments for the command.
            help (str, optional): Defaults to ''. Help Text for the command.
        """
        self.description = description
        self.arguments = arguments
        self.help = help

    def handle(self, app, args):
        """Handle the command execution.

        Args:
            app (App): Main App class
            args (dict): Dictionary with possible passed arguments.

        Raises:
            NotImplementedError: must be implemented
        """
        raise NotImplementedError(
            'handle-Method has not been implemented yet.'
        )
