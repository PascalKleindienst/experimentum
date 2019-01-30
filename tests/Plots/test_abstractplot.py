from experimentum.Plots.Plot import AbstractPlot
import pytest


class TestAbstractPlot(object):
    def setup_mock(self, mocker):
        """ setup_mock abstract command """
        mocker.patch.multiple(AbstractPlot, __abstractmethods__=set())
        return AbstractPlot('repo', 'config')

    def test_init(self, mocker):
        plot = self.setup_mock(mocker)
        assert plot.repo == 'repo'
        assert plot.config == 'config'
        assert plot.type == 'plot'
        assert plot.plot is None

    def test_data(self, mocker):
        plot = self.setup_mock(mocker)
        assert plot.data('experiments') == {'x': 0, 'y': 0, 'z': 0}

    def test_abstract_draw(self, mocker):
        plot = self.setup_mock(mocker)
        with pytest.raises(NotImplementedError):
            plot.draw({})

    def test_abstract_labeling(self, mocker):
        plot = self.setup_mock(mocker)
        with pytest.raises(NotImplementedError):
            plot.labeling()

    def test_abstract_plotting(self, mocker):
        plot = self.setup_mock(mocker)
        with pytest.raises(NotImplementedError):
            plot.plotting()

    def test_abstract_save(self, mocker):
        plot = self.setup_mock(mocker)
        with pytest.raises(NotImplementedError):
            plot.save('foo.svg')

    def test_abstract_show(self, mocker):
        plot = self.setup_mock(mocker)
        with pytest.raises(NotImplementedError):
            plot.show()

