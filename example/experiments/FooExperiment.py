from experimentum.Experiments import Experiment
import random


class FooExperiment(Experiment):

    """Sample Experiment which just adds random numbers to a list."""

    config_file = 'foo.json'

    def reset(self):
        """Reset data structured and values used in each test run."""
        self.my_list = []
        self.range = range(0, 1235)

    def run(self):
        """Perform a test run of the experiment."""
        with self.performance.point('Subtask 1') as subpoint:
            for x in self.range:
                self.my_list.append(x * random.randint(0, 1000))
            subpoint.message('List insert finished')

        with self.performance.point('Subtask 2') as subpoint:
            for x in self.range:
                self.my_list.append(x * random.randint(0, 1000))
            subpoint.message('List insert finished')

        return {
            'random_value': self.my_list[-1],
            'performances': [{
                'label': 'Custom Performance entry',
                'time': 12345,
                'memory': 0,
                'peak_memory': 0,
                'level': 0,
                'type': 'custom'
            }]
        }
