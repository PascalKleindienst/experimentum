"""Interface and Implementation for generating plots and charts.

The default implementation of :py:class:`.AbstractPlot` is the
:py:class:`.Plot` class which internally uses the matplotlib library
to generate the plots. If you want to use another library to generate
your plots you can add a new `CustomPlot` class which implements the
:py:class:`.AbstractPlot` interface. Now your plots need to inherit
from your `CustomPlot` class and you are good to go.
"""
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
        plot (object): Plotting library
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
        self.plot = None

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

    @abstractmethod
    def save(self, filename):
        """Save the plot.

        Args:
            filename (str): Filename to save the plot.

        Raises:
            NotImplementedError: Must implement save method
        """
        raise NotImplementedError('Must implement save method!')

    @abstractmethod
    def show(self):
        """Show the plot.

        Raises:
            NotImplementedError: Must implement show method
        """
        raise NotImplementedError('Must implement show method!')


class Plot(AbstractPlot):

    """Concrete Implementation of the AbstractPlot Interface for a plot class.

    This implementation uses matplotlib to genereate the plots.

    Arguments:
        repo (AbstractRepository): Repository Class to fetch data.
        config (Config): Config data for the plot.
        plot_type (str, optional): Defaults to 'plot'. Type of plot
        plot (matplotlib.pyplot): matplotlib.pyplot module
    """

    def __init__(self, repo, config, plot_type='plot'):
        """Initialize abstract plot.

        Args:
            repo (AbstractRepository): Repository Class to fetch data.
            config (Config): Config data for the plot.
            plot_type (str, optional): Defaults to 'plot'. Type of plot
        """
        super(Plot, self).__init__(repo, config, plot_type)
        self.plot = plt

    def labeling(self):
        """Add labels to the plot."""
        if self.config.get('labels'):
            self.plot.xlabel(self.config.get('labels.x-axis'))
            self.plot.ylabel(self.config.get('labels.y-axis'))

        if self.config.get('title'):
            self.plot.title(self.config.get('title.label'), loc=self.config.get('title.loc'))

        if self.config.get('legend'):
            self.plot.legend(**self.config.get('legend'))

    def plotting(self):
        """Generate the plot, i.e. add labels, titles, legend etc and draw the plot.

        Returns:
            matplotlib.pyplot: Plot object
        """
        self.plot.figure()
        exps = self.repo.get(['name', self.config.get('experiment')])
        plot_data = self.data(exps)

        if isinstance(plot_data, list):
            for plot, data in enumerate(plot_data):
                self.draw(data, plot)
        else:
            self.draw(plot_data)

        if self.config.get('styles.grid', False):
            self.plot.grid(True)

        if self.config.get('styles.axis', False):
            self.plot.axis(self.config.get('styles.axis'))

        if self.config.get('styles.ticks', False):
            self.plot.xticks(**self.config.get('styles.ticks.xticks', {}))
            self.plot.yticks(**self.config.get('styles.ticks.yticks', {}))

        self.labeling()

        return self.plot

    def draw(self, data, plot_idx=None):
        """Draw the plot data.

        Args:
            data (dict): Dictionary with coordinates (e.g. {'x': 0, 'y': 0, 'z': 0})
            plot_idx (integer, optional): Defaults to None. Index for when multiple plots are drawn
        """
        if self.type == 'histogram':
            self.plot.hist(data.get('y'), **self._get_params(plot_idx))
        elif self.type == 'errorbar':
            self.plot.errorbar(data.get('x'), data.get('y'), **self._get_params(plot_idx))
        elif self.type == 'bar':
            self.plot.bar(data.get('x'), data.get('y'), **self._get_params(plot_idx))
        elif self.type == 'pie':
            self.plot.pie(data.get('x'), **self._get_params(plot_idx, ['label']))
        elif self.type == 'scatter':
            self.plot.scatter(data.get('x'), data.get('y'), **self._get_params(plot_idx))
        elif self.type == 'polar':
            self.plot.polar(data.get('theta'), data.get('r'))
        else:
            params = self._get_params(plot_idx)
            fmt = self.config.get('styles.fmt', [])

            if plot_idx is not None and isinstance(fmt, list) and plot_idx < len(fmt):
                fmt = fmt[plot_idx]

            self.plot.plot(data.get('x'), data.get('y'), fmt, **params)

    def save(self, filename):
        """Save the plot.

        Args:
            filename (str): Filename to save the plot.
        """
        self.plot.savefig(filename)

    def show(self):
        """Show the plot."""
        self.plot.show()

    def _get_params(self, plot_idx, remove=None):
        """Get params for the plot.

        Args:
            plot_idx (integer): Index for when multiple plots are drawn.
            remove (list, optional): Defaults to None. List of keys to remove from params.

        Returns:
            dict: Dictionary of params
        """
        _params = {}
        remove = remove if remove is not None else []
        params = self.config.get('params', {})
        params['label'] = self.config.get('styles.label', '')

        for key in remove:
            del params[key]

        for key, values in params.items():
            if plot_idx is not None and isinstance(values, list) and len(values) > plot_idx:
                _params[key] = values[plot_idx]
            else:
                _params[key] = values

        return _params
