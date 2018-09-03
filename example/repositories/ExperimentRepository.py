from experimentum.Storage import AbstractRepository
from repositories.TestCaseRepository import TestCaseRepository


class ExperimentRepository(AbstractRepository.implementation):

    """Repository for the experiments table data."""
    __table__ = 'experiments'
    __relationships__ = {
        'tests': [TestCaseRepository]
    }

    def __init__(self, start=None, finished=None, config_file=None, config_content=None):
        """Set attributes."""
        self.start = start
        self.finished = finished
        self.config_file = config_file
        self.config_content = config_content
