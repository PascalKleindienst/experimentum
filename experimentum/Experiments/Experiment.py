# -*- coding: utf-8 -*-
"""Run experiments and save the results for future analysations.

...

Writing Experiments
-------------------
All Experiments extend the :py:class:`.Experiment` class. Experiments
contain a :py:meth:`~.Experiment.reset` and :py:meth:`~.Experiment.run`
method. Within :py:meth:`~.Experiment.reset` the method, you should
reset/initialize the data structuresand values you want to use in each test run.

The :py:meth:`~.Experiment.run` method should contain the code you want to test.
It should return a dictionary with the values you want to save.

The Reset Method
----------------
As mentioned before the :py:meth:`~.Experiment.reset` should reset/initialize the
data structuresand values you want to use in each test run.

Let's take a look at a basic experiment. Within any of your experiment methods,
you always have access to the :py:attr:`~.Experiment.app` attribute which
provides access to the main app class and to the :py:attr:`~.Experiment.config` which
contains the content of the :py:attr:`~.Experiment.config_file`::

    from experimentum.Experiments import Experiment
    import random


    class FooExperiment(Experiment):

        config_file = 'foo.json'

        def reset(self):
            # use app to create an instance of a custom aliased class
            self.user = self.config.get('user')
            self.some_class = self.app.make('some_class', self.user)
            self.rand = random.randint(0, 10)


The Run Method
--------------
As mentioned before the :py:meth:`~.Experiment.run` method should contain the code
you want to test and return a dictionary with the values you want to save.

Let's take a look at a basic experiment, assuming that you added a ``rand`` attribute to
your TestCaseRepository with a migration::

    from experimentum.Experiments import Experiment
    import random


    class FooExperiment(Experiment):

        config_file = 'foo.json'

        def run(self):
            with self.performance.point('Task to measure some Rscript algo') as point:
                script = self.call('some_script.r')  # prints json to stdout as return value.
                algo_result = script.get_json()
                script.process.wait()  # Wait for child process to terminate.

            # Add a custom performance entry
            return {
                'rand': self.rand,
                'performances': [{
                    'label': 'Custom Rscript measuring',
                    'time': algo_result.get('time'),
                    'memory': 0,
                    'peak_memory': 0,
                    'level': 0,
                    'type': 'custom'
                }]
            }
"""
from __future__ import print_function
import os
import glob
import imp
import subprocess
import json
from datetime import datetime
from six import add_metaclass
from abc import abstractmethod, ABCMeta
from experimentum.Config import Config
from experimentum.Experiments import Performance
from experimentum.cli import print_progress, print_failure
from experimentum.utils import get_basenames


class Script(object):

    """Call another script to run algorithms for your experiment.

    Example::

        script = Script(['Rscript', 'myalgo.r', 'arg1', 'arg2'], verbose=True, shell=True)
        algo_result = script.get_json()
        script.process.wait()  # Wait for child process to terminate.

    Attributes:
        process (subprocess.Popen): Called script.
        output (str): Output of called script.
    """

    def __init__(self, cmd, verbose=False, shell=False, stdout=subprocess.PIPE):
        """Get the return vaue of a process (i.e, the last print statement).

        .. Warning::
            Passing ``shell=True`` can be a security hazard if combined with untrusted input.
            See the warning under `Frequently Used Arguments
            <https://docs.python.org/2/library/subprocess.html#frequently-used-arguments>`_
            for details.

        Args:
            cmd (str, list): Command which you want to call.
            verbose (bool, optional): Defaults to False. Print the cmd output or not.
            shell (bool, optional): Defaults to False. Specifices whether to use the
                shell as the program to execute.
            stdout (int, optional): Defaults to subprocess.PIPE. Specify standard output.
        """
        self.process = subprocess.Popen(cmd, stdout=stdout, shell=shell)
        self.output = None

        # poll will return the exit code if the process is completed otherwise it returns null
        while self.process.poll() is None:
            line = self.process.stdout.readline()
            if not line:
                break
            self.output = line  # last print statement
            if verbose:
                print(line.rstrip().decode('utf-8'))

    def get_json(self):
        """Decode JSON of process output.

        Returns:
            object: Process output
        """
        return json.loads(self.output)


@add_metaclass(ABCMeta)
class Experiment(object):

    """Run experiments and save the results in the data store.

    Attributes:
        app (App): Main Application Class.
        performance (Performance): Performance Profiler.
        config (Config): Hold the experiment configuration.
        show_progress (bool): Flag to show/hide the progress bar.
        hide_performance (bool): Flag to show/hide the performance table.
        config_file (str): Config file to load.
        repos (dict): Experiment and Testcast Repo to save results.
    """
    config_file = None

    def __init__(self, app, path):
        """Init the experiment.

        Args:
            app (App): Main Application class
            path (str): Path to experiments folder
        """
        self.app = app
        self.performance = Performance()
        self.config = Config()
        self.show_progress = False
        self.hide_performance = False
        self.repos = {'experiment': None, 'testcase': None}
        self._path = path

    @staticmethod
    def get_experiments(path):
        """Get experiment names from exp files/classes.

        Args:
            path (str): Path to experiments folder.

        Returns:
            list: Names of experiments
        """
        # TODO: Deprecated remove!
        files = glob.glob(os.path.join(path, '[!_]*.py'))
        return list(map(
            lambda exp: os.path.basename(exp).lower().replace('experiment.py', ''),
            files
        ))

    @staticmethod
    def get_status(app):
        """Get status information about experiments.

        Args:
            app (App): Main Service Provider/Container.

        Returns:
            dict: Dictionary with experiment status
        """
        # Load experiment classes
        path = app.config.get('app.experiments.path', 'experiments')
        exps = get_basenames(app.root, path, 'experiment.py')
        data = {exp.lower(): {'count': 0, 'name': exp} for exp in exps}

        # Load experiment stats
        repo = app.repositories.get('ExperimentRepository')
        rows = repo.all()
        for exp in rows:
            idx = exp.name.lower()
            data[idx]['count'] += 1

            if exp.config_file:
                data[idx]['config_file'] = exp.config_file

        return data

    @staticmethod
    def load(app, path, name):
        """Load and initialize an experiment class.

        Args:
            app (App): Main app calss
            path (str): Path to experiments folder.
            name (str): Name of experiment.

        Returns:
            Experiment: Loaded experiment.
        """
        # TODO: Refactor to use load_class helper
        # Load Experiment File
        files = glob.glob(os.path.join(path, '[!_]*.py'))
        files = list(filter(
            lambda exp: name.lower() == os.path.basename(exp).lower().replace('experiment.py', ''),
            files
        ))

        if not files:
            print_failure(
                'Could not find experiment named "{}" under path "{}"'.format(name, path),
                exit_code=1
            )

        exp = files[0]

        # Init Experiment class if possible
        with open(exp, 'rb') as filehandler:
            try:
                mod = imp.load_source('experiments', exp, filehandler)
                experiment = getattr(mod, os.path.basename(exp)[:-3])
            except Exception as exc:
                print_failure('Could not load experiment. ' + str(exc), exit_code=2)

            if issubclass(experiment, Experiment) is False:
                print_failure(
                    'Experiment must be derived from the experimentum.Experiments.Experiment class',
                    exit_code=3
                )

        return experiment(app, path)

    @staticmethod
    def call(cmd, verbose=False, shell=False):
        """Call another script to run algorithms for your experiment.

        .. Warning::
            Passing ``shell=True`` can be a security hazard if combined with untrusted input.
            See the warning under `Frequently Used Arguments
            <https://docs.python.org/2/library/subprocess.html#frequently-used-arguments>`_
            for details.

        Args:
            cmd (str, list): Command which you want to call.
            verbose (bool, optional): Defaults to False. Print the cmd output or not.
            shell (bool, optional): Defaults to False. Specifices whether to use the
                shell as the program to execute.

        Returns:
            Script: Executed script to get output from
        """
        return Script(cmd, verbose, shell)

    def boot(self):
        """Boot up the experiment, e.g. load config etc."""
        # Load Config/Args for experiment
        if self.config_file:
            try:
                with open(os.path.join(self._path, self.config_file), 'r') as cfg:
                    self.config.set(json.load(cfg))
            except Exception as exc:
                print_failure(exc, 2)

        # Load Experiment and testcase repos
        try:
            self.repos['experiment'] = self.app.repositories.get('ExperimentRepository')
            self.repos['testcase'] = self.app.repositories.get('TestCaseRepository')

            self.repos['experiment'] = self.repos['experiment'].from_dict({
                'name': self.__class__.__name__.replace('Experiment', ''),
                'start': datetime.now(),
                'config_file': self.config_file,
                'config_content': json.dumps(self.config.all()),
                'tests': []
            })
            self.repos['experiment'].create()
        except Exception as exc:
            print_failure(exc, 2)

    def start(self, steps=10):
        """Start the test runs of the experiment.

        Args:
            steps (int, optional): Defaults to 10. How many tests runs should be executed.
        """
        # Booting
        with self.performance.point('Booting Experiment'):
            self.boot()

        # Running tests
        for iteration in self.performance.iterate(1, steps):
            # Reset test state
            self.reset()

            # Run experiment
            with self.performance.point('Runing Experiment'):
                result = self.run()

            # Save Results
            self.save(result, iteration)

            if self.show_progress:
                print_progress(iteration, steps, prefix='Progress:', suffix='Complete')

        # Finished Experiment
        self.repos['experiment'].finished = datetime.now()
        self.repos['experiment'].update()
        if self.hide_performance is False:
            self.performance.results()

    def save(self, result, iteration):
        """Save the test results in the data store.

        Args:
            result (object): Result of experiment test run.
            iteration (int): Number of test run iteration.
        """
        # TODO: Actually saving results and performance values
        # TODO: Wrap saving in try/except statement to catch when saving fails
        # TODO: due to missing tables etc
        data = {
            'experiment_id':  self.repos['experiment'].id,
            'iteration': iteration,
            'performances': []
        }
        data.update(result)
        data['performances'].extend(self.performance.export())

        self.repos['testcase'].from_dict(data).create()

    @abstractmethod
    def reset(self):
        """Reset data structured and values used in the run method."""
        raise NotImplementedError('Must implement reset method.')

    @abstractmethod
    def run(self):
        """Run a test of the experiment."""
        raise NotImplementedError('Must implement run method.')
