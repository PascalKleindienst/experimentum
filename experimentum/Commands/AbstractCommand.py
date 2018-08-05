def command(description='', arguments={}, help=''):
    """Command decorator, creates a Command to use with the CommandManager.

    Keyword Arguments:
        description {str} -- Command Description (default: {''})
        arguments {dict} -- Command Arguments (default: {{}})
        help {str} -- Help Text (default: {''})

    Returns:
        function
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

    Arguments:
        description {str} -- Command description
        arguments {dict} -- Optional Arguments for the command
        help {str} -- Help Text for the command
        args {dict} -- Dictionary with possible passed arguments
    """
    description = ''
    help = ''
    arguments = {}
    args = {}

    def setup(self, description='', arguments={}, help=''):
        """Set up the command.

        Keyword Arguments:
            description {str} -- Command description (default: {''})
            arguments {dict} -- Optional args for the command (default: {{}})
            help {str} -- Help Text for the command (default: {''})
        """
        self.description = description
        self.arguments = arguments
        self.help = help

    def handle(self, app, args):
        """Handle the command execution.

        Arguments:
            app {experimentum.Experiments.App} -- App class
            args {dict} -- Dictionary with possible passed arguments

        Raises:
            NotImplementedError -- must implement abstract method
        """
        raise NotImplementedError(
            'handle-Method has not been implemented yet.'
        )
