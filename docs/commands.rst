============
CLI Commands
============

Migrations
==========

Generating Migrations
---------------------
Use the ``migration:make`` command to create a new :py:class:`.Migration`. This will create the following new :py:class:`.Migration`
class in your ``migrations`` folder. In order to determine the order of the migrations, each migration file name contains a timestamp.

Arguments:

====  ======================
name  Name of the migration
====  ======================

Upgrading Migrations
---------------------
Use the ``migration:up`` command to update to the next migration.

Downgrading Migrations
----------------------
Use the ``migration:down`` command to downgrade to the previous migration.

Refreshing
----------
Use the ``migration:refresh`` command to refresh all migrations, i.e. downgrade all migration and then upgrade all migrations.
This effectivly recreates your entire database.

Status
------
Use the ``migration:status`` command to check which migration did run and which did not.

Experiments
===========
.. automodule:: experimentum.Commands.ExperimentsCommand
