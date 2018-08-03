import argparse
import shutil
import sys
import types
from termcolor import colored
from experimentum.Commands import ColoredHelpFormatter, AbstractCommand


def print_failure(msg):
    """Print a failure message to stder.

    Arguments:
        msg {string} -- Failure message
    """
    try:
        size = shutil.get_terminal_size()[0]  # pylint: disable=no-member
        msg = '{}'.format(msg).center(size, ' ')
        sys.stderr.write('{0}{1}{0}'.format(
            colored(''.center(size, ' '), 'white', 'on_red'),
            colored(msg, 'white', 'on_red', ['bold'])
        ))
    except Exception:
        size = 4
        msg = '{}'.format(msg).center(size, ' ')
        sys.stderr.write('{0}{1}{0}\n'.format(
            colored(''.center(size, ' '), 'white', 'on_red'),
            colored(msg, 'white', 'on_red', ['bold'])
        ))


class CommandManager(object):

    """CommandManager class registers and manages commands.

    Attributes:
        commands {dict} -- Registered commands
    """
    commands = {}

    def __init__(self, prog, description=''):
        """Create and setup up the argument parser and superparsers.

        Arguments:
            prog {string} -- Name of the programm

        Keyword Arguments:
            description {str} -- Description of the programm (default: {''})
        """
        # Init ArgumentParser
        self.parser = argparse.ArgumentParser(
            add_help=False,
            prog=colored(prog, 'yellow'),
            description=colored(description, 'yellow'),
            formatter_class=ColoredHelpFormatter
        )
        self.parser.add_argument(
            '-h', '--help',
            action='help',
            default=argparse.SUPPRESS,
            help='Show this help message and exit.'
        )
        self.parser.add_argument(
            '-v', '--version',
            action='version',
            version='%(prog)s 1.0',
            help="Show program's version number and exit."
        )

        # Colore Titles
        self.parser._positionals.title = colored('Arguments', 'cyan')
        self.parser._optionals.title = colored('Options', 'cyan')

        # Init subparsers
        self.subparsers = self.parser.add_subparsers()

    def add_command(self, name, cmd):
        """Add a new command to the parser.

        Arguments:
            name {string} -- Name of the command
            cmd {func|AbstractCommand} -- Command Handler
        """
        if (
            not isinstance(cmd, types.FunctionType) and
            not issubclass(cmd, AbstractCommand)
        ):
            print_failure("{}-Command must inherit from AbstractCommand!".format(name))
            sys.exit(1)

        # setup command
        cmd = cmd()  # type: AbstractCommand
        command = self.subparsers.add_parser(
            name,
            help=cmd.help,
            description=colored(cmd.description, 'yellow'),
            formatter_class=ColoredHelpFormatter,
            add_help=False
        )
        command.add_argument(
            '-h', '--help',
            action='help',
            default=argparse.SUPPRESS,
            help='Show this help message and exit.'
        )
        command._positionals.title = colored('Arguments', 'cyan')
        command._optionals.title = colored('Options', 'cyan')

        # Add arguments and bind command
        for arg, opt in cmd.arguments.items():
            command.add_argument(arg, **opt)
        command.set_defaults(func=cmd.handle)
        self.commands[name] = command

    def dispatch(self):
        """Use dispatch pattern to invoke class and let it handle the command."""
        # no command selected
        options = self.parser.parse_args()
        if not vars(options):
            print_failure('Please specify a command')
            self.parser.print_help(sys.stderr)
            sys.exit(2)

        # dispatch
        options.func(options)
