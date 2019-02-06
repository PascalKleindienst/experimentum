from experimentum.WebGUI.helpers import ansi_escape, capture_print, CapturedContent
from termcolor import colored
from six import StringIO
import sys


class TestHelpers(object):

    def setup_captured_content(self):
        cp = CapturedContent()
        print('foo')
        print('bar')
        sys.stderr.write('baz')

        return cp

    def test_ansi_escape(self):
        assert ansi_escape(colored('FOO', color='green', on_color='on_red')) == 'FOO'

    def test_captured_print(self):
        with capture_print(True) as cp:
            assert isinstance(cp, CapturedContent)
            assert cp.escape

    def test_captured_content_revert_streams(self):
        cp = CapturedContent()
        assert isinstance(cp.streams['out'], StringIO)
        assert isinstance(cp.streams['err'], StringIO)
        assert sys.stdout is cp.streams['out']
        assert sys.stderr is cp.streams['err']

        cp.revert()
        assert sys.stdout is sys.__stdout__
        assert sys.stderr is sys.__stderr__

    def test_captured_content_get_lines(self):
        cp = self.setup_captured_content()
        assert cp.get_lines() == ['foo', 'bar', 'baz']

    def test_captured_content_get_text(self):
        cp = self.setup_captured_content()
        assert cp.get_text() == 'foo\nbar\nbaz'

    def test_captured_content_has_error(self):
        cp = self.setup_captured_content()
        assert cp.has_error()

        cp.streams['err'] = StringIO()
        assert cp.has_error() is False

    def test_captured_content_clear(self):
        cp = self.setup_captured_content()
        assert cp.streams['out'].getvalue() != ''
        assert cp.streams['err'].getvalue() != ''

        cp.clear()

        assert cp.streams['out'].getvalue() == ''
        assert cp.streams['err'].getvalue() == ''
