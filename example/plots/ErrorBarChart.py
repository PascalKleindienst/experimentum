import numpy as np
from numpy.random import randn
from experimentum.Plots import Plot


class ErrorBarChart(Plot):

    """Simple char with error bars."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: x, y coordinates
        """
        x = np.arange(0, 4, 0.2)
        y = np.exp(-x)
        e1 = 0.1 * np.abs(randn(len(y)))
        e2 = 0.1 * np.abs(randn(len(y)))

        self.config.set('params.xerr', e2)
        self.config.set('params.yerr', [e1, e2])

        return {'x': x, 'y': y}
