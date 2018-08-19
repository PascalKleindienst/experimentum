"""Adding CLI commands to the app and handle their execution."""
import argparse
import shutil
import sys
import types
from termcolor import colored
from experimentum.Commands import AbstractCommand


def print_failure(msg):
    """Print a failure message to stder.

    Args:
        msg (str): Failure message.
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
        app (App): Main App class.
        parser (argparse.ArgumentParser): Main argument parser.
        subparsers (object): Subparser action object to add commands.
        commands (dict): Registered commands.
    """
    commands = {}

    def __init__(self, app, prog, description=''):
        """Create and setup up the argument parser and superparsers.

        Args:
            app (App): Main App class
            prog (str): Name of the programm.
            description (str, optional): Defaults to ''. Description of the programm.
        """
        self.app = app

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

        Args:
            name (str): Name of the command
            cmd (function, AbstractCommand): Command Handler
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
        options = self.parser.parse_args()
        options.func(self.app, options)
        # try:
        #     # dispatch
        #     options = self.parser.parse_args()
        #     options.func(options)
        # except SystemExit:
        #     # no command selected
        #     print_failure('Please specify a command')
        #     self.parser.print_help(sys.stderr)
        #     sys.exit(2)


class ColoredHelpFormatter(argparse.HelpFormatter):

    """HelpFormatter for argparse to create colored output."""

    def _get_help_string(self, action):
        """Color in the default text of the current action."""
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not '==SUPPRESS==':
                defaulting_nargs = ['?', '*']
                if action.nargs in defaulting_nargs:
                    help += colored(' [default: %(default)s]', 'cyan')
        return help

    def _format_action_invocation(self, action):
        """Color in action invation (except for option strings)."""
        txt = super(ColoredHelpFormatter, self)._format_action_invocation(
            action
        )
        if action.option_strings:
            return txt

        return colored(txt, 'green')

    def _format_action(self, action):
        """Color in actions."""
        if action.option_strings:
            help_position = min(
                self._action_max_length + 2,
                self._max_help_position
            )
            action_width = help_position - self._current_indent - 2
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)

            option_string = ', '.join(action.option_strings)
            option = colored(
                "  {:{width}}".format(option_string, width=action_width),
                'green'
            )
            return '{}  {}\n'.format(option, help_text)

        if type(action) == argparse._SubParsersAction:
            # inject new class variable for subcommand formatting
            subactions = action._get_subactions()
            invocations = [
                self._format_action_invocation(a) for a in subactions
            ]
            self._subcommand_max_length = max(len(i) for i in invocations)

        if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
            # format subcommand help line
            subcommand = self._format_action_invocation(action)  # type: str
            width = self._subcommand_max_length
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)

            subcommand = colored(
                "  {:{width}}".format(subcommand, width=width),
                'green'
            )
            return '{}  {}\n'.format(subcommand, help_text)

        elif type(action) == argparse._SubParsersAction:
            # process subcommand help section
            msg = ''
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(ColoredHelpFormatter, self)._format_action(action)

    def add_usage(self, usage, actions, groups, prefix=None):
        """Color in Usage and change format."""
        if prefix is None:
            prefix = colored('Usage: \n  ', 'cyan')
        return super(ColoredHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)
