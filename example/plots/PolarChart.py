import numpy as np
from experimentum.Plots import Plot


class PolarChart(Plot):

    """Simple polar chart with custom plot options."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: polar co-ordinates, r=radius and theta=angle at which r has to be measured from.
        """
        theta = np.arange(0., 2., 1./180.)*np.pi
        r = np.abs(np.sin(5*theta) - 2.*np.cos(theta))

        return {'theta': theta, 'r': r}

    def plotting(self):
        """Generate the plot, i.e. add labels, titles, legend etc and draw the plot.

        Returns:
            matplotlib.pyplot: Plot object
        """
        plt = super(PolarChart, self).plotting()  # plotting defaults

        # add custom options to the plot
        plt.thetagrids(range(45, 360, 90))
        plt.rgrids(np.arange(0.2, 3.1, .7), angle=0)
        plt.text(1.75, 2.25, 'Butterfly')

        return plt
