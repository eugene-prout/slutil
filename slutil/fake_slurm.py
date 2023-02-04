from slutil.abstract_slurm_service import AbstractSlurmService
import random 

class FakeSlurm(AbstractSlurmService):
    @staticmethod
    def get_job_status(job_id: int):
        all_states = ["COMPLETED", "COMPLETING", "FAILED", "CANCELLED+", "PENDING", "PREEMPTED",  "RUNNING", "SUSPENDED", "STOPPED"]
        return "COMPLETED"

    @staticmethod
    def submit_job(sbatch: str) -> int:
        return random.randrange(100000, 999999)

    @staticmethod
    def test_slurm_accessible():
        return True