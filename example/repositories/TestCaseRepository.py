from experimentum.Storage import AbstractRepository
from repositories.PerformanceRepository import PerformanceRepository


class TestCaseRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'testcases'
    __relationships__ = {
        'performances': [PerformanceRepository]
    }

    def __init__(self, experiment_id=None, iteration=None):
        """Set attributes."""
        self.experiment_id = experiment_id
        self.iteration = iteration
