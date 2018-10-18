"""Plot CLI commands to allow you to generate your plots and charts.

Generating plots and charts
---------------------------
Use the ``plots:generate`` command to generate a plot/chart.

Arguments:

====  ==========================================================================
name  Name of the plot/chart *(plot|chart|graph is omitted from the filename)*.
====  ==========================================================================

Options:

-o          Output file where the plot is stored at.
            When omitted the plot is shown directly.
-h, --help  Show the help message.
"""
from experimentum.Commands import command


@command('', help='Generate a plot', arguments={
    'name': {
        'type': str, 'help': 'Name of the plot.'
    },
    '-o': {
        'help': 'Output', 'type': str
    }
})
def generate(app, args):
    """Generate a new plot.

    Args:
        app (App): App Service Container.
        args (argparse.Namespace): Command Arguments and Options.
    """
    plot = app.make('plot', args.name)
    plt = plot.plotting()

    if args.o:
        plt.savefig(args.o)
    else:
        plt.show()
