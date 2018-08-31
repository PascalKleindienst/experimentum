from experimentum.Storage import AbstractRepository


class TestCaseRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'testcases'

    def __init__(self, id=None):
        """Set attributes."""
        self.id = id
