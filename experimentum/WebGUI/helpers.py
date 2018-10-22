"""Helper functions for the webinterface."""
import re
import sys
from six import StringIO
from contextlib import contextmanager

ansi_pattern = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')


def ansi_escape(text):
    """Remove ansi colors from text.

    Args:
        text (str): Text to escape

    Returns:
        str: escaped text
    """
    return ansi_pattern.sub('', text)


@contextmanager
def capture_print(escape=False):
    """Capture prints to stdout and stderr.

    Args
        escape (bool, optional): Defaults to False. Whether to escape ansi sequences or not.
    """
    capturer = CapturedContent(escape)

    try:
        yield capturer
    finally:
        capturer.revert()


class CapturedContent(object):

    """Capture prints to stdout and stderr.

    Arguments:
        streams (dict): Output streams for stdout and stderr
        escape (bool): Flag to indicate if streams should be escaped.
    """

    def __init__(self, escape=True):
        """Set streams for stdout and stderr.

        Args:
            escape (bool, optional): Defaults to True. Whether to escape ansi sequences or not.
        """
        self.streams = {'out': StringIO(), 'err': StringIO()}
        self.escape = escape

        # capture stdout and stderr
        sys.stdout = self.streams['out']
        sys.stderr = self.streams['err']

    def revert(self):
        """Revert back to default stdout and stderr streams."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def get_lines(self):
        """Get merged lines for stdout and stderr.

        Returns:
            list: list of lines
        """
        return self._merge()

    def get_text(self):
        """Get all prints/writes to stdout and stderr.

        Returns:
            str: text
        """
        return '\n'.join(self.get_lines())

    def _prepare_lines(self, lines):
        """Strip and escape lines if needed.

        Args:
            lines (list): list of lines

        Returns:
            list: list of prepared lines
        """
        return list(map(lambda l: ansi_escape(l).strip() if self.escape else l.strip(), lines))

    def _merge(self):
        """Merge stdout and stderr together.

        Returns:
            list: list of lines
        """
        output = self._prepare_lines(self.streams['out'].getvalue().splitlines())
        output.extend(self._prepare_lines(self.streams['err'].getvalue().splitlines()))

        return output
