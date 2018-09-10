# -*- coding: utf-8 -*-
"""Management of all migrations.

Handles actions like upgrade, downgrading, keeping track of
which migrations did run and which not. Used by :py:mod:`.MigrationCommand`.
"""
from __future__ import print_function
import os
import glob
import imp
import inflection
import datetime
from tabulate import tabulate
from termcolor import colored
from experimentum.cli import print_failure


class Migrator(object):

    """Management of all migrations.

    Attributes:
        path (str): Path to the migrations folder.
    """

    @staticmethod
    def get_migration_files(path):
        """Get all of the migration files in a given path.

        Args:
            path (str): Path to migrations folder

        Returns:
            list: list of migration files
        """
        files = glob.glob(os.path.join(path, '[0-9]*_*.py'))

        if not files:
            return []

        files = list(map(lambda f: os.path.basename(f).replace('.py', ''), files))
        files = sorted(files)

        return files

    def __init__(self, path, app):
        """Set the path for the migrations.

        Args:
            path (str): Path to the migrations folder.
        """
        self.path = path

        # create .version file
        name = '{}/.version'.format(self.path)

        if not os.path.isfile(name):
            with open(name, 'w+') as file:
                file.write('')

        # load migrations
        self.migrations = {}
        names = self.get_migration_files(path)

        for name in names:
            file = os.path.join(path, '%s.py' % name)
            with open(file, 'rb') as filehandler:
                mod = imp.load_source('migrations', file, filehandler)
                migration = getattr(mod, inflection.camelize(name[15:]))
                self.migrations[name] = migration(app)

    def status(self):
        """Print the current status of which migrations did run and which not."""
        # check whether migration did run or not
        migrated = self._get_migrated_revisions()
        migrations = self.get_migration_files(self.path)
        status = [
            [colored(m, 'cyan'), colored('Yes', 'green')] if m[:14] in migrated
            else [colored(m, 'cyan'), colored('No', 'red')]
            for m in migrations
        ]

        headers = [colored('Migration', 'yellow'), colored('Ran?', 'yellow')]
        print(tabulate(status, headers=headers, tablefmt='psql'))

    def make(self, name):
        """Make a new migration file.

        Args:
            name (str): Name for the migration.
        """
        name = ''.join(list(filter(lambda x: x.isalpha() or x == '_', name.replace(' ', '_'))))
        migration = inflection.camelize(name)
        revision = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = "{}/{}_{}.py".format(self.path, revision, name.lower())

        stub = ''
        with open(os.path.join(os.path.dirname(__file__), 'migration.stub'), 'r') as content:
            stub = content.read()

        with open(filename, 'w+') as file:
            file.write(stub.format(migration=migration, name=name, revision=revision))
            print(colored('› Migration created successfully!', 'green'))

    def up(self, migration=None):
        """Upgrade to a new migration revision.

        Args:
            migration (Migration, optional): Defaults to None. The Migration Class to upgrade to.

        Raises:
            TypeError: if migration is not a valid migration
        """
        # Select first migration to run
        if migration is None:
            migrated = self._get_migrated_revisions()
            migrations = self.get_migration_files(self.path)
            migration = [mig for mig in migrations if mig[:14] not in migrated]

            if len(migration) is 0:
                print(colored('› Migrations are all up to date.', 'green'))
                return

            migration = self.migrations.get(migration[0])

        # update migration
        try:
            migration.up()
            self._update_revision(migration.revision)
            print(colored('› Migrated', 'green'), colored(migration, 'cyan'))
        except Exception as exc:
            print_failure('Error while ugrading migration {}: {}'.format(migration, exc), 1)

    def down(self, migration=None):
        """Downgrade to an old migration revision.

        Args:
            migration (Migration, optional): Defaults to None. The Migration Class to upgrade to.

        Raises:
            TypeError: if migration is not a valid migration
        """
        # Select first migration to run
        if migration is None:
            # get finished migrations
            migrated = self._get_migrated_revisions()
            migrations = self.get_migration_files(self.path)[::-1]
            migration = [mig for mig in migrations if mig[:14] in migrated]

            if len(migration) is 0:
                print(colored('× There are no migrations to downgrade.', 'red'))
                return

            migration = self.migrations.get(migration[0])

        # downgrade migration
        try:
            migration.down()
            self._update_revision(migration.revision, delete=True)
            print(colored('› Migrated', 'green'), colored(migration, 'cyan'))
        except Exception as exc:
            print_failure('Error while downgrading migration {}: {}'.format(migration, exc), 1)

    def refresh(self):
        """Rerun all migrations."""
        migrated = self._get_migrated_revisions()
        migrations = self.get_migration_files(self.path)

        # downgrade all migrations
        print(colored('--- Downgrading Migrations ---', 'yellow'))
        for migration in migrations[::-1]:
            if migration[:14] in migrated:
                self.down(self.migrations.get(migration))

        # run all up migrations
        print(colored('\n--- Upgrading Migrations ---', 'yellow'))
        for migration in migrations:
            self.up(self.migrations.get(migration))

        return True

    def _update_revision(self, revision, delete=False):
        """Update the revision number.

        Args:
            revision (str): The new revision
            delete (bool, optional): Defaults to False. Whether to delete the revision or not.
        """
        fname = os.path.join(self.path, '.version')
        revisions = self._get_migrated_revisions()

        with open(fname, 'w+') as filehandler:
            if delete:
                # print('remove revision')
                revisions.remove(revision)
            else:
                # print('add revision')
                revisions.append(revision)

            filehandler.write('|'.join(revisions))

    def _get_migrated_revisions(self):
        """Get old migrations revisions.

        Returns:
            list
        """
        old = []
        with open('{}/.version'.format(self.path), 'r') as filehandler:
            old = filehandler.read().split('|')
        return old
