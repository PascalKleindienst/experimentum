from experimentum.Storage import AbstractRepository
from repositories.PerformanceRepository import PerformanceRepository


class TestCaseRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'testcases'
    __relationships__ = {
        'performances': [PerformanceRepository]
    }

    def __init__(self, iteration, random_value, experiment_id=None):
        """Set attributes."""
        self.iteration = iteration
        self.random_value = random_value
        self.experiment_id = experiment_id
