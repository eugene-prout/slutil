from abc import ABC, abstractmethod


class AbstractVCS(ABC):
    @staticmethod
    @abstractmethod
    def get_current_commit() -> str:
        raise NotImplementedError
