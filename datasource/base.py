"""Common read-only data source contract.

Sources return normalized payload dictionaries. The contract intentionally has
no write, command, pairing, or therapy-control method.
"""
from abc import ABC, abstractmethod

class ReadOnlyDataSource(ABC):
    @property
    @abstractmethod
    def source_name(self): ...

    @abstractmethod
    def read_sensor(self): ...

    @abstractmethod
    def read_status(self): ...

    def capabilities(self):
        return {
            "read_sensor": True,
            "read_status": True,
            "writes": False,
            "commands": False,
            "pairing": False,
            "therapy_operations": False,
        }
