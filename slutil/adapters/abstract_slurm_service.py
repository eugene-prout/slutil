from abc import ABC, abstractmethod


class AbstractSlurmService(ABC):
    @staticmethod
    @abstractmethod
    def get_job_status(job_id: int) -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def submit_job(sbatch: str) -> int:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def test_slurm_accessible() -> bool:
        raise NotImplementedError
