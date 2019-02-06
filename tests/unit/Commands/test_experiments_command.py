import argparse
import pytest
from experimentum.Commands.ExperimentsCommand import run, status
from experimentum.Experiments import Experiment


class TestExperimentsCommand(object):
    def setup_mocks(self, mocker):
        exp_mock = mocker.patch('experimentum.Experiments.Experiment')
        exp_mock.start = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=exp_mock)

        return exp_mock, app_mock

    def test_run_n_times(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(n=42, name='f', config=None, progress=False, hide_performance=False)

        run().handle(app_mock, args)
        exp_mock.start.assert_called_once_with(42)

    def test_run_load_config(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(n=1, name='f', config='foo.json', progress=False, hide_performance=False)

        run().handle(app_mock, args)
        assert exp_mock.config_file == 'foo.json'

    def test_run_show_progress(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(n=1, name='f', config=None, progress=True, hide_performance=False)

        run().handle(app_mock, args)
        assert exp_mock.show_progress is True

    def test_run_hide_performance(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(n=1, name='f', config=None, progress=False, hide_performance=True)

        run().handle(app_mock, args)
        assert exp_mock.hide_performance is True

    def test_status(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace()
        mocker.patch.object(Experiment, 'get_status')
        Experiment.get_status.return_value = {'foo': {'count': 0, 'name': 'Foo Exp'}, 'bar': {'count': 1, 'name': 'Bar Exp'}}

        status().handle(app_mock, args)
        Experiment.get_status.assert_called_once_with(app_mock)

    def test_status_with_no_exps(self, mocker):
        exp_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace()

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            status().handle(app_mock, args)
            exp_mock.get_status.assert_called_once_with(app_mock)

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2
