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
        self.n = self.config.get('n', 0)

    def run(self):
        """Run the Experiment, i.e. calculated the nth fibonacci number."""
        print(colored('* Calculating fibonacci sequence', 'green'))

        val = -1
        with self.performance.point('Calculating Fibonacci Sequence'):
            val = fib(self.n, self.fib_sequence)

        print(' > Sequence = {}'.format(colored(self.fib_sequence, 'cyan')))
        print(' > fib({}) = {}\n'.format(self.n, colored(val, 'cyan')))

        return {
            'value': val
        }
