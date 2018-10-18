from experimentum.Plots import Plot


class PieChart(Plot):

    """Simple pie chart."""

    def data(self, experiments):
        """Gather data.

        Args:
            experiments (AbstractRepository): Repository with current experiment

        Returns:
            dict: the wedge sizes. The fractional area of each wedge is given by x/sum(x)
        """
        self.config.set('params.labels', ["Swiss", "Austria", "Spain", "Italy", "France", "Sweden"])
        self.config.set('params.explode',  [0.2, 0.1, 0, 0, 0.1, 0])
        self.config.set('params.autopct', '%1.1f%%')

        return {'x': [4, 9, 21, 55, 30, 18]}
