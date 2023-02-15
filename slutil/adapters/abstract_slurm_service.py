from abc import ABC, abstractmethod
from typing import Optional

class AbstractSlurmService(ABC):
    @staticmethod
    @abstractmethod
    def get_job_status(job_id: int) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def submit_job(sbatch: str, dependency_type: Optional[str], dependency_list: list[int]) -> int:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def test_slurm_accessible() -> bool:
        raise NotImplementedError
