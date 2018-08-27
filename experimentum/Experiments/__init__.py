"""Provides the main entry point and some utilities for running experiments.

Import :py:mod:`.App`, :py:mod:`Experiment` and :py:mod:`.Performance` so that
they can be easly imported by other packages/modules.
"""
# flake8: noqa
from .Performance import Performance
from .Experiment import Experiment, Script
from .App import App
