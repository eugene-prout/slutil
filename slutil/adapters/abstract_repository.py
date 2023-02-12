from abc import ABC, abstractmethod
from slutil.model.Record import Record


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, job: Record) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, job_id: int) -> Record:
        raise NotImplementedError

    @abstractmethod
    def get_deleted(self, job_id: int) -> Record:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Record]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self):
        raise NotImplementedError
