"""Import classes for easier importing by other packages/modules."""
# flake8: noqa
from .Experiments import *
from .Config import *

##################
# Helper Methods #
##################
def config():
    """Shortcut for getting the config instance."""
    return app().config
