from experimentum.Experiments import Experiment
import sys
import os


class FooExperiment(Experiment):
    def reset(self):
        """Reset data structured and values used in each test run."""
        self.script_output = None

    def run(self):
        """Perform a test run of the experiment."""
        script = self.call(['python', os.path.join(os.path.dirname(__file__), '_experiment.py')])
        self.script_output = script.get_json()


class TestExperiments(object):
    def test_experiment_run(self, cli_app, app_files):
        """
        GIVEN the framework is installed and the experiments and testcases tables exist
        WHEN a user runs an experiment
        THEN the experiment and testcases should be saved in the database
        """
        # Create Experiment file
        app_files.create_from_stub(cli_app.config_path, 'FooExperiment', 'experiments/{name}.py')

        # User runs the experiment
        sys.argv = ['main.py', 'experiments:run', 'foo', '--n=2']
        cli_app.run()

        # check database
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM experiments;').first()[0] == 1
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 2
        assert list(cli_app.store.session.execute('SELECT iteration FROM testcases;')) == [
            (1,), (2,)
        ]

    def test_experiment_save(self, cli_app, app_files):
        """
        GIVEN the framework is installed and the experiments and testcases tables exist,
            and the testcases table has a bar column
        WHEN a user runs an experiment
        THEN the experiment results should be saved in the database
        """
        # Create Experiment file
        app_files.create_from_stub(cli_app.config_path, 'FooExperiment', 'experiments/{name}.py')

        # User runs the experiment
        sys.argv = ['main.py', 'experiments:run', 'foo', '--n=1']
        cli_app.run()

        # check database
        assert cli_app.store.session.execute('SELECT COUNT(*) FROM testcases;').first()[0] == 1
        assert list(cli_app.store.session.execute('SELECT bar FROM testcases;')) == [(1,)]

    def test_experiment_implement(self, cli_app, app_files):
        """
        GIVEN the framework is installed and the experiments and testcases tables exist,
            and the testcases table has a bar column
        WHEN a user runs an experiment which calls a python script via the CLI
        THEN the python results should be returned to the experiment
        """
        # Create and simulate the Experiment run, because otherwise we could not really check
        exp = FooExperiment(cli_app, cli_app.config_path)
        exp.start(1)

        # Check if script output is correctly passed to the experiment
        assert exp.script_output == [1, 2, 3]

    def test_experiment_profiling(self, cli_app, app_files):
        """
        GIVEN the framework is installed and the standard tables exist
        WHEN the user wants to profile a specific part of the experiment
        THEN the benchmarked point is saved in the performance table
        """
        # Create Experiment file
        app_files.create_from_stub(
            cli_app.config_path,
            'FooExperimentProfiling',
            'experiments/FooExperiment.py'
        )

        # User runs the experiment
        sys.argv = ['main.py', 'experiments:run', 'foo', '--n=1']
        cli_app.run()

        # Check if performance is saved
        session = cli_app.store.session
        assert session.execute('SELECT COUNT(*) FROM performance;').first()[0] == 3
        assert list(session.execute('SELECT label FROM performance;'))[2] == ('Test-Abschnitt',)

        data = list(session.execute(
            'SELECT level, type, memory, time FROM performance WHERE label = "Test-Abschnitt";'
        ).first())
        assert data[0] == 1
        assert data[1] == 'point'
        assert data[2] >= 0.0
        assert data[3] >= 0.0

    def test_experiment_visualization(self, cli_app, app_files):
        """
        GIVEN the framework is installed and the standard tables exist
        WHEN the user generates a new plot image
        THEN plot should be saved as a valid image/svg file
        """
        import imghdr

        # User runs the plot generation
        sys.argv = ['main.py', 'plot:generate', 'foo', '-o', 'test.png']
        cli_app.run()

        # check file
        assert os.path.isfile('test.png')
        assert os.path.getsize('test.png') > 1024
        assert imghdr.what('test.png') == 'png'

        # cleanup
        os.remove('test.png')
