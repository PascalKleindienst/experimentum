from experimentum.Plots import Plot
import matplotlib.pyplot as plt


class TestPlot(object):
    def setup_plot(self, mocker, plot_type='plot'):
        repo_mock = mocker.MagicMock()
        config_mock = mocker.MagicMock()
        plt_mock = mocker.patch('matplotlib.pyplot')

        plot = Plot(repo_mock, config_mock, plot_type=plot_type)
        plot.plot = plt_mock

        return plot

    def _draw_plot(self, mocker, data, conf, plt_idx=None, plot_type='plot'):
        plot = self.setup_plot(mocker, plot_type)
        plot.config.get.side_effect = lambda key, default=None: conf.get(key, default)
        plot.draw(data, plt_idx)
        return plot

    def test_init(self):
        from types import ModuleType

        plot = Plot('repo', 'config')
        assert plot.repo == 'repo'
        assert plot.config == 'config'
        assert plot.type == 'plot'
        assert isinstance(plot.plot, ModuleType)

    def test_labeling_labels(self, mocker):
        plot = self.setup_plot(mocker)

        # Mock cfg class content
        cfg = {
            'labels': True, 'title': False, 'legend': False,
            'labels.x-axis': 'x-axis', 'labels.y-axis': 'y-axis',
        }
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plot.labeling()
        plot.plot.xlabel.assert_called_once_with('x-axis')
        plot.plot.ylabel.assert_called_once_with('y-axis')
        plot.plot.title.assert_not_called()
        plot.plot.legend.assert_not_called()

    def test_labeling_title(self, mocker):
        plot = self.setup_plot(mocker)

        # Mock cfg class content
        cfg = {
            'labels': False, 'title': True, 'legend': False,
            'title.label': 'Title', 'title.loc': 'tr',
        }
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plot.labeling()
        plot.plot.title.assert_called_once_with('Title', loc='tr')
        plot.plot.xlabel.assert_not_called()
        plot.plot.ylabel.assert_not_called()
        plot.plot.legend.assert_not_called()

    def test_labeling_legend(self, mocker):
        plot = self.setup_plot(mocker)

        # Mock cfg class content
        cfg = {'labels': False, 'title': False, 'legend': {'loc': 'upper center'}}
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plot.labeling()
        plot.plot.legend.assert_called_once_with(loc='upper center')
        plot.plot.xlabel.assert_not_called()
        plot.plot.ylabel.assert_not_called()
        plot.plot.title.assert_not_called()

    def test_plotting(self, mocker):
        plot = self.setup_plot(mocker)
        plot.draw = mocker.MagicMock()

        plot.config.get.side_effect = lambda key, default=None: {}.get(key, default)

        plt = plot.plotting()

        assert plt == plot.plot
        plot.draw.assert_called_once_with({'y': 0, 'x': 0, 'z': 0})

    def test_plotting_multiple(self, mocker):
        plot = self.setup_plot(mocker)
        plot.data = mocker.MagicMock(return_value=[{'x': 0, 'y': 0}, {'x': 1, 'y': 1}])
        plot.draw = mocker.MagicMock()

        plot.config.get.side_effect = lambda key, default=None: {}.get(key, default)

        plt = plot.plotting()

        plot.draw.assert_any_call({'y': 0, 'x': 0}, 0)
        plot.draw.assert_any_call({'y': 1, 'x': 1}, 1)
        assert 2 == plot.draw.call_count

    def test_plotting_grid(self, mocker):
        plot = self.setup_plot(mocker)
        plot.draw = mocker.MagicMock()

        cfg = {'styles.grid': True}
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plt = plot.plotting()
        plt.grid.assert_called_once_with(True)

    def test_plotting_axis(self, mocker):
        plot = self.setup_plot(mocker)
        plot.draw = mocker.MagicMock()

        cfg = {'styles.axis': [0, 5, -1, 64]}
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plt = plot.plotting()
        plt.axis.assert_called_once_with([0, 5, -1, 64])

    def test_plotting_ticks(self, mocker):
        plot = self.setup_plot(mocker)
        plot.draw = mocker.MagicMock()

        cfg = {
            'styles.ticks': True,
            'styles.ticks.xticks': {'foo': 'bar'},
            'styles.ticks.yticks': {'foo': 'bar'}
        }
        plot.config.get.side_effect = lambda key, default=None: cfg.get(key, default)

        plt = plot.plotting()
        plt.xticks.assert_called_once_with(foo='bar')
        plt.yticks.assert_called_once_with(foo='bar')

    def test_draw(self, mocker):
        conf = {'styles.fmt': 'r--', 'params': {'ecolor': 'green'}}
        plot = self._draw_plot(mocker, {'x': 0, 'y': 0}, conf)

        plot.plot.plot.assert_called_once_with(0, 0, 'r--', ecolor='green', label='')

    def test_draw_multiple(self, mocker):
        conf = {'styles.fmt': ['r--', 'g++'], 'params': {'ecolor': 'green'}}
        plot = self._draw_plot(mocker, {'x': 0, 'y': 0}, conf, 1)

        plot.plot.plot.assert_called_once_with(0, 0, 'g++', ecolor='green', label='')

    def test_draw_histogram(self, mocker):
        plot = self._draw_plot(mocker, {'y': 0}, {}, plot_type='histogram')
        plot.plot.hist.assert_called_once_with(0, label='')

    def test_draw_errorbar(self, mocker):
        plot = self._draw_plot(mocker, {'x': 1, 'y': 0}, {}, plot_type='errorbar')
        plot.plot.errorbar.assert_called_once_with(1, 0, label='')

    def test_draw_bar(self, mocker):
        plot = self._draw_plot(mocker, {'x': 1, 'y': 0}, {}, plot_type='bar')
        plot.plot.bar.assert_called_once_with(1, 0, label='')

    def test_draw_pie(self, mocker):
        plot = self._draw_plot(mocker, {'x': 1}, {}, plot_type='pie')
        plot.plot.pie.assert_called_once_with(1)

    def test_draw_scatter(self, mocker):
        plot = self._draw_plot(mocker, {'x': 1, 'y': 0}, {}, plot_type='scatter')
        plot.plot.scatter.assert_called_once_with(1, 0, label='')

    def test_draw_polar(self, mocker):
        plot = self._draw_plot(mocker, {'theta': 1, 'r': 0}, {}, plot_type='polar')
        plot.plot.polar.assert_called_once_with(1, 0)

    def test_save(self, mocker):
        plot = self.setup_plot(mocker)
        plot.save('foo.svg')
        plot.plot.savefig.assert_called_once_with('foo.svg')

    def test_show(self, mocker):
        plot = self.setup_plot(mocker)
        plot.show()
        plot.plot.show.assert_called_once_with()
