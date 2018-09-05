from experimentum.Storage import AbstractRepository
from repositories.TestCaseRepository import TestCaseRepository


class ExperimentRepository(AbstractRepository.implementation):

    """Repository for the experiments table data."""
    __table__ = 'experiments'
    __relationships__ = {
        'tests': [TestCaseRepository]
    }

    def __init__(self, name, config_file, start, config_content=None, finished=None):
        """Set attributes."""
        self.name = name
        self.config_file = config_file
        self.start = start
        self.config_content = config_content
        self.finished = finished
