"""Migration CLI commands to allow you to version control your database schema.

With Migrations your team is able to easily modify and share the
database schema to stay up to date. Migrations are typically paired
with the :py:mod:`.Schema` Builder which is inspired by the
`Laravel Schema Builder <https://laravel.com/docs/5.6/migrations#tables>`_
to easly manage your database's schema.


Generating Migrations
---------------------
Use the ``migration:make`` command  to create a new :py:class:`.Migration`. This will create the
following new :py:class:`.Migration` class in your ``migrations`` folder. In order to determine
the order of the migrations, each migration file name contains a timestamp.

Arguments:

====  ======================
name  Name of the migration
====  ======================


Migration Structure
-------------------
Each :py:class:`.Migration` class contains two methods: :py:meth:`.Migration.up` and
:py:meth:`.Migration.down`. In the :py:meth:`.Migration.up` method you add new tables,
columns, or indexes to your database. In the :py:meth:`.Migration.down` method you
should revert those changed made in the :py:meth:`.Migration.up` method.

Inside the :py:class:`.Migration` class you have access to the :py:mod:`.Schema` Builder
to easily create and modify tables. For more information check out its documentation:
:py:mod:`.Schema`

Running Migrations
------------------
To run the latest outstanding :py:class:`.Migration`, just use the ``migration:up`` command.
To revert the last :py:class:`.Migration` operation, just use the ``migration:down`` command.

To roll back all migrations and then execute all migrations, just use the ``migration:refresh``
command. This command effectively re-creates your entire database.

To see the status of the migrations, just use the ``migration:status`` command.
This would output something like this::

    |-------------------------------------------+--------|
    | Migration                                 | Ran?   |
    |-------------------------------------------+--------|
    | 20180814111005_create_users_table         | Yes    |
    | 20180815101334_add_avater_to_users_table  | No     |
    |-------------------------------------------+--------|
"""
from experimentum.Commands import command


@command(
    'Displays which migrations where migrated and which ones not.',
    help='Show the migration status.'
)
def status(app):
    """Show the status of the migrations.

    Arguments:
        app (App): Main Service Container
    """
    app.make('migrator').status()


@command(
    'Reset all migrations and then run them again to rebuild the data schema.',
    help='Rebuild the data schema (clears database).'
)
def refresh(app):
    """Refresh all migrations.

    Arguments:
        app (App): Main Service Container
    """
    app.make('migrator').refresh()


@command(
    'Upgrade the oldes migration which needs to be upgraded.',
    help='Upgrade oldest migration.'
)
def up(app):
    """Upgrade the oldes migration which needs to be upgraded.

    Arguments:
        app (App): Main Service Container
    """
    app.make('migrator').up()


@command(
    'Downgrade latest migration',
    help='Downgrade the latest migration which can be downgraded.'
)
def down(app):
    """Downgrade the latest migration which can be downgraded.

    Arguments:
        app (App): Main Service Container
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
        app (App): Main Service Container
        args (dict): Additional args
    """
    app.make('migrator').make(args.name.lower())
