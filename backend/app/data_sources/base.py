from abc import ABC, abstractmethod


class DataSource(ABC):
    """
    Base class for all external data sources.
    """


    @abstractmethod
    def fetch(self):
        pass


    @abstractmethod
    def validate(self, data):
        pass
