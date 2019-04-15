from experimentum.Experiments import Experiment
from experimentum.cli import print_failure
from termcolor import colored


def fib(n, seq):
    """Calculate the nth fibonacci number.

    Args:
        n (int)
        seq (list): List of fibonacci numbers

    Returns:
        int
    """
    if n < 0:
        print_failure('Incorrect Input', exit_code=1)
    elif n <= len(seq):
        return seq[n - 1]

    tmp = fib(n - 1, seq) + fib(n - 2, seq)
    seq.append(tmp)
    return tmp


class FibExperiment(Experiment):

    """Experiment which tests the the fibonacci algorithm."""

    config_file = 'foo.json'

    def reset(self):
        """Reset data structure and values used in each test run."""
        print(colored('* Resetting fibonacci sequence', 'green'))
        self.fib_sequence = [0, 1]

    def run(self):
        val = -1
        n = self.config.get('n', 0)
        print(colored('* Calculating fibonacci sequence', 'green'))
        with self.performance.point('Calculating Fibonacci Sequence'):
            val = fib(n, self.fib_sequence)

        print(' > Sequence = {}'.format(colored(self.fib_sequence, 'cyan')))
        print(' > fib({}) = {}\n'.format(n, colored(val, 'cyan')))

        return {
            'value': val
        }
