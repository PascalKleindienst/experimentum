from experimentum.Storage import AbstractRepository
from repositories.PerformanceRepository import PerformanceRepository


class TestCaseRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'testcases'
    __relationships__ = {
        'performances': [PerformanceRepository]
    }

    def __init__(self, iteration, value, experiment_id=None):
        """Set attributes."""
        self.iteration = iteration
        self.value = value
        self.experiment_id = experiment_id
