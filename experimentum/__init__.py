"""Import classes for easier importing by other packages/modules."""
# flake8: noqa
from .Experiments import App, Performance, Experiment
from .Config import Config, Loader
from .Commands import AbstractCommand, CommandManager, MigrationCommand
from .Storage import AbstractStore, Blueprint, Column, ForeignKey, Migration, Migrator,\
    Schema, ColumnFactory, Platform, SQLitePlatform, Store

##################
# Helper Methods #
##################
# def config(get=None, default=None):
#     """Shortcut for getting the config instance."""
#     return app().config.get(get, default) if get else app().config
