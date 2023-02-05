from slutil.adapters.abstract_slurm_service import AbstractSlurmService
import subprocess
import re


class SlurmService(AbstractSlurmService):
    @staticmethod
    def get_job_status(job_id: int):
        if not SlurmService.test_slurm_accessible():
            raise OSError("Slurm accessed required but cannot access Slurm")

        regex_pattern = r"^(\s*JobID\s*JobName\s*Partition\s*Account\s*AllocCPUS\s*State\s*ExitCode\s*)(-*\s*){7}(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*){7}$"
        output = subprocess.check_output(["sacct", "-j", str(job_id)]).strip().decode()
        regex_match = re.match(regex_pattern, output)
        if regex_match:
            return regex_match.group(8).strip()
        raise OSError("sacct command has unexpected output")

    @staticmethod
    def submit_job(sbatch: str) -> int:
        if not SlurmService.test_slurm_accessible():
            raise OSError("Slurm accessed required but cannot access Slurm")

        proc = subprocess.run(
            f"sbatch {sbatch}", check=True, capture_output=True, shell=True
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
