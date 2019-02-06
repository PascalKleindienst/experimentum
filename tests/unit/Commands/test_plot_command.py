import argparse
from experimentum.Commands.PlotCommand import generate


class TestPlotCommand(object):
    def setup_mocks(self, mocker):
        plt_mock = mocker.patch('experimentum.Plots.Plot')
        plt_mock.plotting = mocker.MagicMock()
        plt_mock.save = mocker.MagicMock()
        plt_mock.show = mocker.MagicMock()
        app_mock = mocker.patch('experimentum.Experiments.App')
        app_mock.make = mocker.MagicMock(return_value=plt_mock)

        return plt_mock, app_mock

    def test_save_plot(self, mocker):
        plt_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(name='foo_plot', o='foo.svg')

        generate().handle(app_mock, args)
        app_mock.make.assert_called_once_with('plot', 'foo_plot')
        plt_mock.plotting.assert_called_once_with()
        plt_mock.save.assert_called_once_with('foo.svg')

    def test_show_plot(self, mocker):
        plt_mock, app_mock = self.setup_mocks(mocker)
        args = argparse.Namespace(name='foo_plot')

        generate().handle(app_mock, args)
        app_mock.make.assert_called_once_with('plot', 'foo_plot')
        plt_mock.plotting.assert_called_once_with()
        plt_mock.show.assert_called_once_with()
        plt_mock.save.assert_not_called()
