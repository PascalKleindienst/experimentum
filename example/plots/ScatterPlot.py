from numpy.random import randn, rand
from experimentum.Plots import Plot


class ScatterPlot(Plot):

    """Simple scatter plot."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: x, y coordinates
        """
        self.config.set('params.s', 50*randn(1000))  # size
        self.config.set('params.c', rand(1000))  # colors

        return {'x':  randn(1000), 'y': randn(1000)}
