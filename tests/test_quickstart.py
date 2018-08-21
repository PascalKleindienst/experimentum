from experimentum.quickstart import main
import sys
import os


def _side_effects(msg, default=None):
    _input = TestQuickstart.side_effects.pop(0)
    return default if _input == '' else _input


class TestQuickstart(object):
    side_effects = []

    def _patch(self, mocker, root, inputs):
        sys.argv = ['main.py', '--root', root]
        TestQuickstart.side_effects = inputs
        mocker.patch('experimentum.quickstart._get_input', side_effect=_side_effects)

    def test_defaults(self, mocker, tmpdir):
        root = tmpdir.strpath
        self._patch(mocker, root, ['', '', '', 'TestApp', '', ''])

        main()

        assert os.path.isdir(os.path.join(root, 'config')) is True
        assert os.path.isdir(os.path.join(root, 'migrations')) is True
        assert os.path.isdir(os.path.join(root, 'logs')) is True
        assert os.path.isfile(os.path.join(root, 'config', 'app.json')) is True
        assert os.path.isfile(os.path.join(root, 'config', 'storage.json')) is True
        assert os.path.isfile(os.path.join(root, 'main.py')) is True

    def test_user_inputs(self, mocker, tmpdir):
        root = tmpdir.strpath
        self._patch(mocker, root, ['cfg', 'database', 'logging', 'TestApp', '', 'foo.py'])

        main()

        assert os.path.isdir(os.path.join(root, 'cfg')) is True
        assert os.path.isdir(os.path.join(root, 'database')) is True
        assert os.path.isdir(os.path.join(root, 'logging')) is True
        assert os.path.isfile(os.path.join(root, 'cfg', 'app.json')) is True
        assert os.path.isfile(os.path.join(root, 'cfg', 'storage.json')) is True
        assert os.path.isfile(os.path.join(root, 'foo.py')) is True