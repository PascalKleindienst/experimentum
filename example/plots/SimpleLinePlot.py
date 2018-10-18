import numpy as np
from experimentum.Plots import Plot


class SimpleLinePlot(Plot):

    """Simple line plot."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: x, y coordinates
        """
        # evenly sampled time at 200ms intervals
        t = np.arange(0., 5., 0.2)

        # return either {x: t, y: t} for single line
        # or [{x:t, y:t}, {x:t, y:t**2}, {x:t, y:t**3}] for multiple lines
        return [
            {'x': t, 'y': t},  # Line 1
            {'x': t, 'y': t**2},  # Line 2
            {'x': t, 'y': t**3},  # Line 3
        ]
