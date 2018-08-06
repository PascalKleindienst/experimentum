from experimentum.Commands import command


@command(
    'Displays which migrations where migrated and which ones not.',
    help='Show the migration status.'
)
def status(app, args):
    """Show the status of the migrations.

    Arguments:
        app {experimentum.Experiments.App}
        args {dict} -- Additional args
    """
    app.make('migrator').status()


@command(
    'Reset all migrations and then run them again to rebuild the data schema.',
    help='Rebuild the data schema (clears database).'
)
def refresh(app, args):
    """Refresh all migrations.

    Arguments:
        app {experimentum.Experiments.App}
        args {dict} -- Additional args
    """
    app.make('migrator').refresh()


@command(
    'Upgrade the oldes migration which needs to be upgraded.',
    help='Upgrade oldest migration.'
)
def up(app, args):
    """Upgrade the oldes migration which needs to be upgraded.

    Arguments:
        app {experimentum.Experiments.App}
        args {dict} -- Additional args
    """
    app.make('migrator').up()


@command(
    'Downgrade latest migration',
    help='Downgrade the latest migration which can be downgraded.'
)
def down(app, args):
    """Downgrade the latest migration which can be downgraded.

    Arguments:
        app {experimentum.Experiments.App}
        args {dict} -- Additional args
    """
    app.make('migrator').down()


@command(
    'Create a new migration file in the migrations folder.',
    arguments={'name': {'help': 'Name of the migration'}},
    help='Make a new migration.'
)
def make(app, args):
    """Make a new migration file.

    Arguments:
        app {experimentum.Experiments.App}
        args {dict} -- Additional args
    """
    app.make('migrator').make(args.name.lower())
