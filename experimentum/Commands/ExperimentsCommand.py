"""Experiment CLI commands to allow you to run and manage your experiments.

Running experiments
-------------------
Use the ``experiments:run`` command to run an experiment.

Arguments:

====  ======================
name  Name of the experiment
====  ======================

Options:

--config=file       Use alternative config file *(relative to experiments folder)*.
--progress          Toggle visibility of the progress bar.
--n=number          Run the experiment *n* times.
--hide_performance  Hides the performance table.
-h, --help          Show the help message.

Listing experiments
-------------------
Use the ``experiments:list`` command to list status information about all experiments.

Options:

-h, --help  Show the help message.
"""
from tabulate import tabulate
from termcolor import colored
from experimentum.cli import print_failure
from experimentum.Commands import command
from experimentum.Experiments import Experiment


@command('Load an run an experiment', help='Run an experiment', arguments={
    'name': {
        'type': str, 'help': 'Name of the experiment.'
    },
    '--n': {
        'type': int, 'default': 100, 'help': 'Run the experiment *n* times.'
    },
    '--config': {
        'type': str, 'help': 'Use alternative config file relative to experiments folder.'
    },
    '--progress': {
        'action': 'store_true', 'help': 'Toggle visibility of the progress bar'
    },
    '--hide_performance': {
        'action': 'store_true', 'help': 'Hides the performance table.'
    }
})
def run(app, args):
    """Load an run an experiment.

    Args:
        app (App): App Service Container.
        args (argparse.Namespace): Command Arguments and Options.
    """
    experiment = app.make('experiment', args.name)

    if args.config is not None:
        experiment.config_file = args.config

    if args.progress is True:
        experiment.show_progress = True

    if args.hide_performance is True:
        experiment.hide_performance = True

    experiment.start(args.n)


@command('Gather status informations about all available experiments', help='List experiments')
def status(app, args):
    """List experiment status.

    Args:
        app (App): App Service Container.
        args (argparse.Namespace): Command Arguments and Options.
    """
    data = []
    headers = [
        colored('Experiment', 'yellow'),
        colored('Config File', 'yellow'),
        colored('Times Executed', 'yellow')
    ]

    try:
        exps = Experiment.get_status(app)
        for experiment in exps.values():
            data.append([
                colored(experiment['name'], 'cyan'),
                colored(experiment.get('config_file'), 'cyan'),
                colored(experiment['count'], 'cyan')
            ])
    except Exception as exc:
        print_failure(exc, 2)

    print(tabulate(data, headers=headers, tablefmt='psql'))
