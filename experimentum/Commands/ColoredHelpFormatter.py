import argparse
from termcolor import colored


class ColoredHelpFormatter(argparse.HelpFormatter):

    """HelpFormatter for argparse to create colored output."""

    def _get_help_string(self, action):
        """Color in the default text of the current action.

        Arguments:
            action {argparse.Action}

        Returns:
            argparse.Action
        """
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not '==SUPPRESS==':
                defaulting_nargs = ['?', '*']
                if action.nargs in defaulting_nargs:
                    help += colored(' [default: %(default)s]', 'cyan')
        return help

    def _format_action_invocation(self, action):
        """Color in action invation (except for option strings).

        Arguments:
            action {argparse.Action}

        Returns:
            string
        """
        txt = super(ColoredHelpFormatter, self)._format_action_invocation(
            action
        )
        if action.option_strings:
            return txt

        return colored(txt, 'green')

    def _format_action(self, action):
        """Color in actions.

        Arguments:
            action {argparse.Action}

        Returns:
            string
        """
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
