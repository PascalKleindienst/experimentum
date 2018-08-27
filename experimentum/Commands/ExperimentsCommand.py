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
"""
from experimentum.Commands import command


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
        app (App): Main App Class.
        args (argparse.Namespace): Command Arguments and Options
    """
    experiment = app.make('experiment', args.name)

    if args.config is not None:
        experiment.config_file = args.config

    if args.progress is True:
        experiment.show_progress = True

    if args.hide_performance is True:
        experiment.hide_performance = True

    experiment.start(args.n)
