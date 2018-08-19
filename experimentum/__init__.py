"""Import classes for easier importing by other packages/modules."""
# flake8: noqa
from .Experiments import *
from .Config import *
from .Commands import *
from .Storage import *

##################
# Helper Methods #
##################
# def config(get=None, default=None):
#     """Shortcut for getting the config instance."""
#     return app().config.get(get, default) if get else app().config
