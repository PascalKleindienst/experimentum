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
        mocker.patch('experimentum.quickstart.get_input', side_effect=_side_effects)

    def test_defaults(self, mocker, tmpdir):
        root = tmpdir.strpath
        self._patch(mocker, root, ['', '', '', '', '', 'TestApp', '', ''])

        main()

        assert os.path.isdir(os.path.join(root, 'config')) is True
        assert os.path.isdir(os.path.join(root, 'migrations')) is True
        assert os.path.isdir(os.path.join(root, 'repositories')) is True
        assert os.path.isdir(os.path.join(root, 'experiments')) is True
        assert os.path.isdir(os.path.join(root, 'logs')) is True
        assert os.path.isfile(os.path.join(root, 'config', 'app.json')) is True
        assert os.path.isfile(os.path.join(root, 'config', 'storage.json')) is True
        assert os.path.isfile(os.path.join(root, 'repositories', '__init__.py')) is True
        assert os.path.isfile(os.path.join(root, 'repositories', 'ExperimentRepository.py')) is True
        assert os.path.isfile(os.path.join(root, 'repositories', 'TestCaseRepository.py')) is True
        assert os.path.isfile(os.path.join(root, 'experiments', '__init__.py')) is True
        assert os.path.isfile(os.path.join(root, 'main.py')) is True

    def test_user_inputs(self, mocker, tmpdir):
        root = tmpdir.strpath
        self._patch(mocker, root, ['cfg', 'database', 'repos', 'exps', 'logging', 'TestApp', '', 'foo.py'])

        main()

        assert os.path.isdir(os.path.join(root, 'cfg')) is True
        assert os.path.isdir(os.path.join(root, 'database')) is True
        assert os.path.isdir(os.path.join(root, 'repos')) is True
        assert os.path.isdir(os.path.join(root, 'exps')) is True
        assert os.path.isdir(os.path.join(root, 'logging')) is True
        assert os.path.isfile(os.path.join(root, 'cfg', 'app.json')) is True
        assert os.path.isfile(os.path.join(root, 'cfg', 'storage.json')) is True
        assert os.path.isfile(os.path.join(root, 'repos', '__init__.py')) is True
        assert os.path.isfile(os.path.join(root, 'repos', 'ExperimentRepository.py')) is True
        assert os.path.isfile(os.path.join(root, 'repos', 'TestCaseRepository.py')) is True
        assert os.path.isfile(os.path.join(root, 'exps', '__init__.py')) is True
        assert os.path.isfile(os.path.join(root, 'foo.py')) is True
