from numpy.random import randn
from experimentum.Plots import Plot


class HistogramChart(Plot):

    """Simple histogram chart."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: y coordinates
        """
        self.config.set('params.bins', 25)
        return {'y': randn(1000)}
