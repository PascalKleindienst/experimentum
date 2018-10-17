from __future__ import unicode_literals
from six import add_metaclass
from abc import abstractmethod, ABCMeta
import matplotlib.pyplot as plt


@add_metaclass(ABCMeta)
class AbstractPlot(object):

    """Abstract Interface for a plot class.

    Arguments:
        repo (AbstractRepository): Repository Class to fetch data.
        config (Config): Config data for the plot.
        plot_type (str, optional): Defaults to 'plot'. Type of plot
    """

    def __init__(self, repo, config, plot_type='plot'):
        """Initialize abstract plot.

        Args:
            repo (AbstractRepository): Repository Class to fetch data.
            config (Config): Config data for the plot.
            plot_type (str, optional): Defaults to 'plot'. Type of plot
        """
        self.repo = repo
        self.config = config
        self.type = plot_type

    def data(self, experiments):
        """Return Data for the plot.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            list|dict: x,y,z values or list of x,y,z coordinates (e.g. {'x': 0, 'y': 0, 'z': 0})
        """
        return {'x': 0, 'y': 0, 'z': 0}

    @abstractmethod
    def draw(self, data, plot_idx=None):
        """Draw the plot data.

        Args:
            data (dict): Dictionary with coordinates (e.g. {'x': 0, 'y': 0, 'z': 0})
            plot_idx (integer, optional): Defaults to None. Index for when multiple plots are drawn

        Raises:
            NotImplementedError: Must implement draw method
        """
        raise NotImplementedError('Must implement draw method!')

    @abstractmethod
    def labeling(self):
        """Add labels to the plot.

        Raises:
            NotImplementedError: Must implement labeling method
        """
        raise NotImplementedError('Must implement labeling method!')

    @abstractmethod
    def plotting(self):
        """Generate the plot, i.e. add labels, titles, legend etc and draw the plot.

        Returns:
            object: Plot object

        Raises:
            NotImplementedError: Must implement plotting method
        """
        raise NotImplementedError('Must implement plotting method!')


class Plot(AbstractPlot):

    """Concrete Implementation of the AbstractPlot Interface for a plot class.

    This implementation uses matplotlib to genereate the plots.

    Arguments:
        repo (AbstractRepository): Repository Class to fetch data.
        config (Config): Config data for the plot.
        plot_type (str, optional): Defaults to 'plot'. Type of plot
    """

    def labeling(self):
        """Add labels to the plot."""
        if self.config.get('labels'):
            plt.xlabel(self.config.get('labels.x-axis'))
            plt.ylabel(self.config.get('labels.y-axis'))

        if self.config.get('title'):
            plt.title(**self.config.get('title'))

        if self.config.get('legend'):
            plt.legend(**self.config.get('legend'))

    def plotting(self):
        """Generate the plot, i.e. add labels, titles, legend etc and draw the plot.

        Returns:
            matplotlib.pyplot: Plot object
        """
        exps = self.repo.get(['name', self.config.get('experiment')])
        plot_data = self.data(exps)

        if isinstance(plot_data, list):
            for plot, data in enumerate(plot_data):
                self.draw(data, plot)
        else:
            self.draw(plot_data)

        if self.config.get('styles.grid', False):
            plt.grid(True)

        if self.config.get('styles.axis', False):
            plt.axis(self.config.get('styles.axis'))

        if self.config.get('styles.ticks', False):
            plt.xticks(**self.config.get('styles.ticks.xticks', {}))
            plt.yticks(**self.config.get('styles.ticks.yticks', {}))

        self.labeling()

        return plt

    def draw(self, data, plot_idx=None):
        """Draw the plot data.

        Args:
            data (dict): Dictionary with coordinates (e.g. {'x': 0, 'y': 0, 'z': 0})
            plot_idx (integer, optional): Defaults to None. Index for when multiple plots are drawn
        """
        params = self.config.get('params', {})
        params['fmt'] = self.config.get('styles.fmt', '')
        params['label'] = self.config.get('styles.label', '')

        if self.type == 'histogram':
            plt.hist(data.get('y'), bins=self.config.get('params.bins'))
        elif self.type == 'errorbar':
            plt.errorbar(data.get('x'), data.get('y'), **params)
        elif self.type == 'bar':
            del params['fmt']
            plt.bar(data.get('x'), data.get('y'), **params)
        else:
            for key, values in params.items():
                if isinstance(values, list) and len(values) > plot_idx:
                    params[key] = values[plot_idx]
            fmt = params['fmt']
            del params['fmt']

            plt.plot(data.get('x'), data.get('y'), fmt, **params)
