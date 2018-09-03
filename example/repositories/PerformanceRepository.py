from experimentum.Storage import AbstractRepository


class PerformanceRepository(AbstractRepository.implementation):

    """Repository for the performance table data."""
    __table__ = 'performance'

    def __init__(
        self, label=None, level=None, type=None, time=None, memory=None, peak_memory=None
    ):
        """Set attributes."""
        self.label = label
        self.level = level
        self.type = type
        self.time = time
        self.memory = memory
        self.peak_memory = peak_memory
