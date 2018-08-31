# -*- coding: utf-8 -*-
"""Some CLI Helpers."""
import sys
import six
import shutil
import logging
from termcolor import colored


def get_input(msg, default=None):
    """Get the user input.

    Args:
        msg (str): Message
        default (object, optional): Default to None. Default value if nothing is entered

    Returns:
        object: User Input
    """
    # Default value if skipped
    if default is not None:
        return six.moves.input(colored("› {} [{}]: ".format(msg, default), 'green')) or default

    # Required input
    value = six.moves.input(colored("› {}: ".format(msg), 'green'))
    while value is '':
        print(colored("× Please specify a value!", 'red'))
        value = six.moves.input(colored("› {}: ".format(msg), 'green'))

    return value


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """Call in a loop to create terminal progress bar.

    https://gist.github.com/aubricus/f91fb55dc6ba5557fbab06119420dd6a

    Args:
        iteration (int): current iteration
        total (int): total iterations
        prefix (str, optional): Defaults to ''. Prefix string
        suffix (str, optional): Defaults to ''. Suffix string
        decimals (int, optional): Defaults to 1. Positive number of decimals in percent complete.
        bar_length (int, optional): Defaults to 100. Character length of bar.
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s\n' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def print_failure(msg, exit_code=None):
    """Print a failure message to stder.

    Args:
        msg (str): Failure message.
    """
    try:
        msg_format = '{0}{1}{0}'
        size = shutil.get_terminal_size()[0]  # pylint: disable=no-member
    except Exception:
        msg_format = '{0}{1}{0}\n'
        size = 4

    msg = '{}'.format(msg).center(size, ' ')
    sys.stderr.write(msg_format.format(
        colored(''.center(size, ' '), 'white', 'on_red'),
        colored(msg, 'white', 'on_red', ['bold'])
    ))
    logging.getLogger('experimentum').critical(msg)

    if exit_code is not None:
        sys.exit(exit_code)
