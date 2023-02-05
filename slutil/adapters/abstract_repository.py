from abc import ABC, abstractmethod
from slutil.model.Record import Record


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, job: Record):
        raise NotImplementedError

    @abstractmethod
    def get(self, job_id: int) -> Record:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Record]:
        raise NotImplementedError
