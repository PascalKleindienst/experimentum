import numpy as np
from numpy.random import randn
from experimentum.Plots import Plot


class BarChart(Plot):

    """Simple Bar Chart with error boxes."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            list: list of x, y coordinates
        """
        values = {'A': 40, 'B': 70, 'C': 30, 'D': 85}
        ticks = {
            'xticks': {'ticks': np.arange(len(values)), 'labels': values.keys()},
            'yticks': {'ticks': list(values.values())}
        }
        self.config.set('styles.ticks', ticks)
        self.config.set('params.yerr', list(13.5 * np.abs(randn(len(values)))))

        return [
            {'x': i, 'y': values[key]} for i, key in enumerate(values)
        ]
