from experimentum.Plots import Plot
import json


class ExampleBarChart(Plot):

    """Simple Bar Chart with repository usage."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            list: list of x, y coordinates
        """
        labels = []
        values = []
        for exp in experiments:
            # Get which nth fib number was used from exp config
            x = json.loads(exp.config_content).get('n', -1)

            # get the average 'value' of test runs for each experiment
            test_vals = list(map(lambda test: test.value, exp.tests))
            labels.append(int(sum(test_vals) / len(test_vals)))

            # add to data
            values.append({
                'x': x,
                'y': len(exp.tests)  # number of test runs
            })

        self.config.set('styles.label', labels)

        return values
