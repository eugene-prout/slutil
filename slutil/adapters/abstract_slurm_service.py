from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

class AbstractSlurmService(ABC):
    @staticmethod
    @abstractmethod
    def get_job_status(job_id: int, allow_none: bool) -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def submit_job(sbatch: str, dependency_type: Optional[str], dependency_list: list[int]) -> int:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def test_slurm_accessible() -> bool:
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    def recover_job_data(job_id: int, allow_none: bool) -> Optional[dict]:
        raise NotImplementedError

class SlurmError(Exception):
    pass

class SlurmNotAccessibleError(Exception):
    pass