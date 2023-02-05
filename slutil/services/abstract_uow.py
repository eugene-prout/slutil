from abc import ABC, abstractmethod
from slutil.adapters.abstract_repository import AbstractRepository


class AbstractUnitOfWork(ABC):
    jobs: AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
