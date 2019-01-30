"""Factory to load and init plot classes."""
from experimentum.cli import print_failure
from experimentum.utils import find_files, load_class
from experimentum.Plots import AbstractPlot


class Factory(object):

    """Create instances of plot classes based on their name.

    Attributes:
        app (App): Main Service Container.
    """

    def __init__(self, app):
        """Init Plot factory.

        Args:
            app (App): Main Service Container.
        """
        self.app = app

    def create(self, name):
        """Create a new plot class instance.

        Args:
            name (str): Name of the plot.

        Returns:
            AbstractPlot: Plot Class
        """
        # Get plot data from config and validate it
        data = self.parse(name)
        config = self.validate(data)

        # Load plot class
        path = self.app.config.get('app.plots.path', 'plots')
        plots = find_files(self.app.root, path, name, '(plot|chart|graph).py')

        if not plots:
            print_failure(
                'Could not find plot named "{}" under path "{}"'.format(name, path),
                exit_code=1
            )
        plot = load_class(plots[0], path, AbstractPlot)

        # Init plot class
        return plot(
            self.app.repositories.get('ExperimentRepository'),
            config,
            config.get('type', 'plot')
        )

    def parse(self, plot):
        """Parse the config file for the current plot.

        Args:
            plot (str): Name of the plot.

        Returns:
            object: Config data for the plot
        """
        config = self.app.config.get('plots.{}'.format(plot), None)

        if config is None:
            print_failure(
                'Could not parse config for plot "%s". '
                'Make sure it exists in the config file!' % plot,
                exit_code=1
            )

        return config

    def validate(self, data):
        """Validate the config data and save it in the Config Container if valid.

        Args:
            data (object): Config Data

        Returns:
            Config: Config Data for the plot.
        """
        # TODO: Actually validate config data before saving
        config = self.app.make('config')
        config.set(data)

        return config
