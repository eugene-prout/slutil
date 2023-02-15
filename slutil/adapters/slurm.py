from slutil.adapters.abstract_slurm_service import AbstractSlurmService
import subprocess
import re
from typing import Optional

class SlurmService(AbstractSlurmService):
    @staticmethod
    def get_job_status(job_id: int):
        if not SlurmService.test_slurm_accessible():
            raise OSError("Slurm accessed required but cannot access Slurm")

        regex_pattern = rf"({job_id})\s+([\w\.]*)\s*(\w*)\s*(\w*)\s*(\d*)\s*([\w\+]*)\s*([\w:]*)"
        output = subprocess.check_output(["sacct", "-j", str(job_id)]).strip().decode()
        regex_match = re.search(regex_pattern, output)
        if regex_match:
            return regex_match.group(6).strip()
        raise OSError("sacct command has unexpected output")

    @staticmethod
    def submit_job(sbatch: str, dependency_type: Optional[str], dependency_list: list[int]) -> int:
        if not SlurmService.test_slurm_accessible():
            raise OSError("Slurm accessed required but cannot access Slurm")

        command =  f"sbatch {sbatch}"
        if dependency_type:
            if dependency_type == "singleton":
                command += f" --dependency={dependency_type}"
            else:
                command += f" --dependency={dependency_type}:{':'.join(map(str, dependency_list))}"
        
        proc = subprocess.run(
           command, check=True, capture_output=True, shell=True
        )
        # proc.stdout should be "Submitted batch job XXXXXX"
        regex_match = re.match(
            r"^(Submitted batch job )(\d*)$", proc.stdout.decode("utf-8")
        )
        if regex_match:
            return int(regex_match.group(2))
        raise OSError("sbatch command has unexpected output")

    @staticmethod
    def test_slurm_accessible():
        try:
            subprocess.run(["sinfo"], capture_output=True, check=True)
            return True
        except:
            return False
