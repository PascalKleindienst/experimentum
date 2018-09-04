# -*- coding: utf-8 -*-
from experimentum.Experiments import Experiment, Script
import pytest
import json


class TestExperiments(object):
    def _setup(self, mocker, tmpdir):
        with tmpdir.join('cfg.json').open('w+') as fh:
            json.dump({'foo': 'bar'}, fh)

        mocker.patch.multiple(Experiment, __abstractmethods__=set())
        app_mock = mocker.patch('experimentum.Experiments.App')
        exp = Experiment(app_mock, tmpdir.strpath)
        exp.config_file = 'cfg.json'

        return exp

    def test_abstract_reset(self, tmpdir, mocker):
        exp = self._setup(mocker, tmpdir)

        with pytest.raises(NotImplementedError):
            exp.reset()

    def test_abstract_run(self, tmpdir, mocker):
        exp = self._setup(mocker, tmpdir)

        with pytest.raises(NotImplementedError):
            exp.run()

    def test_boot(self, tmpdir, mocker):
        exp = self._setup(mocker, tmpdir)
        exp.boot()
        assert exp.config.all() == {'foo': 'bar'}

    def test_boot_load_cfg_failure(self, tmpdir, mocker, capsys):
        exp = self._setup(mocker, tmpdir)
        exp.config_file = 'bar.json'
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            exp.boot()
        assert 'No such file or directory' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_fail_load(self, mocker, tmpdir, capsys):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Experiment.load(mocker.patch('experimentum.Experiments.App'), tmpdir.strpath, 'Foo')

        assert 'Could not find experiment named "{}" under path "{}"'.format('Foo', tmpdir.strpath) in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_fail_import_module(self, mocker, tmpdir, capsys):
        with tmpdir.join('FooExperiment.py').open('w+') as fh:
            fh.write('')

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Experiment.load(mocker.patch('experimentum.Experiments.App'),tmpdir.strpath, 'Foo')

        assert 'Could not load experiment.' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_fail_import_class(self, mocker, tmpdir, capsys):
        with tmpdir.join('FooExperiment.py').open('w+') as fh:
            fh.write('class FooExperiment(object): pass')

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Experiment.load(mocker.patch('experimentum.Experiments.App'),tmpdir.strpath, 'Foo')

        assert 'Experiment must be derived from the experimentum.Experiments.Experiment class' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 3

    def test_load_exp(self, mocker, tmpdir, capsys):
        with tmpdir.join('FooExperiment.py').open('w+') as fh:
            fh.write(
                "from experimentum.Experiments import Experiment\n"
                "class FooExperiment(Experiment):\n"
                "   def run(self): pass \n"
                "   def reset(self): pass"
            )

        assert isinstance(Experiment.load(mocker.patch('experimentum.Experiments.App'), tmpdir.strpath, 'Foo'), Experiment)

    def test_call_command(self, mocker, tmpdir):
        exp = self._setup(mocker, tmpdir)
        mocker.patch('experimentum.Experiments.Script', '__init__', lambda *args, **kwargs: None)

        assert isinstance(exp.call('ls'), Script)
