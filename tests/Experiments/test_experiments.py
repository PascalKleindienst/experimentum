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
        exp.repos['testcase'] = mocker.MagicMock()
        exp.repos['experiment'] = mocker.MagicMock()
        exp.repos['experiment'].id = 42

        return exp

    def _create_exp(self, mocker, tmpdir, result):
        exp = self._setup(mocker, tmpdir)
        exp.boot = mocker.MagicMock()
        exp.reset = mocker.MagicMock()
        exp.run = mocker.MagicMock(return_value=result)
        exp.save = mocker.MagicMock()
        exp.performance.results = mocker.MagicMock()

        return exp


    def test_get_status(self, tmpdir, mocker):
        with tmpdir.join('FooExperiment.py').open('w+') as fh:
            fh.write('#Foo')

        with tmpdir.join('BarExperiment.py').open('w+') as fh:
            fh.write('#Bar')

        rows_mock = mocker.MagicMock()
        rows_mock.name = 'Foo'
        rows_mock.config_file = 'foo.json'
        repo_mock = mocker.MagicMock()
        repo_mock.all = mocker.MagicMock(return_value=[rows_mock])
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.config.get = mocker.MagicMock(return_value=tmpdir.strpath)
        app_mock.repositories.get = mocker.MagicMock(return_value=repo_mock)


        data = Experiment.get_status(app_mock)
        assert data['foo']['count'] is 1
        assert data['foo']['name'] == 'Foo'
        assert data['foo']['config_file'] == 'foo.json'
        assert data['bar']['count'] is 0
        assert data['bar']['name'] == 'Bar'

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

        assert 'Could not load file' in capsys.readouterr().err
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_fail_import_class(self, mocker, tmpdir, capsys):
        with tmpdir.join('FooExperiment.py').open('w+') as fh:
            fh.write('class FooExperiment(object): pass')

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            Experiment.load(mocker.patch('experimentum.Experiments.App'),tmpdir.strpath, 'Foo')

        assert 'FooExperiment must be derived from the experimentum.Experiments.Experiment.Experiment class' in capsys.readouterr().err
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

    def test_start(self, mocker, tmpdir, capsys):
        exp = self._create_exp(mocker, tmpdir, {'foo': 'bar'})

        exp.start(steps=3)

        exp.boot.assert_called_once_with()
        exp.repos['experiment'].update.assert_called_once_with()
        exp.performance.results.assert_called_once_with()
        assert exp.reset.call_count == 3
        assert exp.run.call_count == 3
        assert exp.save.call_count == 3
        assert 'Progress' not in capsys.readouterr().out

    def test_start_hide_performance(self, mocker, tmpdir):
        exp = self._create_exp(mocker, tmpdir, {'foo': 'bar'})

        exp.hide_performance = True
        exp.start(steps=1)

        exp.performance.results.assert_not_called()

    def test_start_show_progress(self, mocker, tmpdir, capsys):
        exp = self._create_exp(mocker, tmpdir, {'foo': 'bar'})

        exp.show_progress = True
        exp.start(steps=1)

        assert 'Progress' in capsys.readouterr().out

    def test_start_empty_results(self, mocker, tmpdir, capsys):
        exp = self._create_exp(mocker, tmpdir, {})

        exp.start(steps=1)
        assert 'Experiment returned an empty result.' in capsys.readouterr().out

    def test_save(self, mocker, tmpdir):
        exp = self._setup(mocker, tmpdir)
        exp.performance = mocker.patch('experimentum.Experiments.Performance')
        exp.performance.export.return_value = [{'performance': 'foo'}]

        exp.save({'foo': 'bar', 'bar': {'foobar': 'baz'}}, 2)

        exp.performance.export.assert_called_once_with()
        exp.repos['testcase'].from_dict.assert_called_once_with({
            'experiment_id':42,
            'iteration': 2,
            'performances': [{'performance': 'foo'}],
            'foo': 'bar',
            'bar': {'foobar': 'baz'}
        })
