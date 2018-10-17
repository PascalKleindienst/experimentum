from experimentum.Commands import command


@command('', help='Generate a plot', arguments={
    'name': {
        'type': str, 'help': 'Name of the plot.'
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

    # plt.savefig('plot123.svg')
    plt.show()
