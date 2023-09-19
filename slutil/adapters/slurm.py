from __future__ import annotations
import datetime

from attr import dataclass

from slutil.adapters.abstract_slurm_service import AbstractSlurmService, SlurmError, SlurmNotAccessibleError
import subprocess
import re
from typing import Optional
import logging

from slutil.adapters.datetime_util import calculate_timedelta_offset_from_now, parse_slurm_duration


class SlurmService(AbstractSlurmService):
    @staticmethod
    def get_job_status(job_id: int, allow_none: bool):
        logging.debug(
            "getting latest status of job %d, allow_none: %s", job_id, allow_none
        )
        if not SlurmService.test_slurm_accessible():
            raise SlurmNotAccessibleError("Slurm accessed required but cannot access Slurm")

        regex_pattern = rf"^(JobID\|State\|\n)({job_id})\|(PENDING|RUNNING|SUSPENDED|COMPLETED|CANCELLED by \d*|FAILED|TIMEOUT|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE|OUT_OF_MEMORY)\|$"

        command = ["sacct", "-j", str(job_id), "-o", "JOBID,State", "--parsable", "-X"]
        logging.debug("running command: , `%s`", " ".join(command))

        try:
            output = subprocess.check_output(command).strip().decode()
        except subprocess.CalledProcessError as e:
            logging.error("subprocess error when running command")
            raise SlurmError(f"Error running {e.cmd}, process error message: {e.stderr}")

        logging.debug("command returned: %s", output)

        regex_match = re.fullmatch(regex_pattern, output)
        logging.debug("regex match: %s", regex_match)

        if regex_match:
            status = regex_match.group(3).strip()
            logging.debug("extracted status: %s", status)
            if "CANCELLED by" in status:
                status = status[:9]
                logging.debug("detected cancelled by, extracted status: %s", status)
            return status

        if allow_none:
            logging.debug("returning None (allowed)")
            return None

        logging.debug("regex match is None and None is not allowed, raising OSError")
        raise OSError(
            f"sacct command has unexpected output \nexpected:\n{regex_match}\ngot:\n{output}"
        )

    @staticmethod
    def submit_job(
        sbatch: str, dependency_type: Optional[str], dependency_list: list[int]
    ) -> int:
        if not SlurmService.test_slurm_accessible():
            raise SlurmNotAccessibleError("cannot access slurm. Ensure slurm can be accessed before submitting a job.")

        logging.debug("submitting slurm job")

        command = f"sbatch"
        if dependency_type:
            dependency = ""
            if dependency_type == "singleton":
                dependency = f" --dependency={dependency_type}"
            else:
                dependency = f" --dependency={dependency_type}:{':'.join(map(str, dependency_list))}"
            logging.debug("adding dependency section: %s", dependency)
            command += dependency
        command += f" {sbatch}"
        logging.debug("running command: %s", command)

        try:
            proc = subprocess.run(command, check=True, capture_output=True, shell=True)
            logging.debug("command returned: %s", proc.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            logging.error("subprocess error when running command")
            raise SlurmError(f"Error running {e.cmd}, process error message: {e.stderr}")



        # proc.stdout should be "Submitted batch job XXXXXX"
        regex_match = re.match(
            r"^(Submitted batch job )(\d*)$", proc.stdout.decode("utf-8")
        )
        logging.debug("regex matched: %s", regex_match)

        if regex_match:
            return int(regex_match.group(2))

        logging.debug("no regex match, raising OSError")
        raise OSError("sbatch command has unexpected output")

    @staticmethod
    def test_slurm_accessible():
        logging.debug("testing slurm access with `sinfo`")
        try:
            subprocess.run(["sinfo"], capture_output=True, check=True)
            logging.debug("successfully accessed slurm")
            return True
        except:
            logging.warning("cannot access slurm")
            return False


    @staticmethod
    def recover_job_data(job_id: int, allow_none: bool) -> Optional[RecoveredSlurmData]:
        logging.debug(
            "getting latest status of job %d, allow_none: %s", job_id, allow_none
        )
        if not SlurmService.test_slurm_accessible():
            raise SlurmNotAccessibleError("Slurm accessed required but cannot access Slurm")

        regex_pattern = (rf"^(JobID\|Submit\|State\|Comment\|\n)"
                         f"({job_id})"
                         r"\|([^\n]+)"
                         r"\|(PENDING|RUNNING|SUSPENDED|COMPLETED|CANCELLED by \d*|FAILED|TIMEOUT|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE|OUT_OF_MEMORY)"
                         r"\|([^\n]+)"
                         r"$")

        command = ["sacct", "-j", str(job_id), "-o", "JOBID,Submit,State,Comment", "--parsable", "-X"]
        logging.debug("running command: , `%s`", " ".join(command))

        try:
            output = subprocess.check_output(command).strip().decode()
        except subprocess.CalledProcessError as e:
            logging.error("subprocess error when running command")
            raise SlurmError(f"Error running {e.cmd}, process error message: {e.stderr}")

        logging.debug("command returned: %s", output)

        regex_match = re.fullmatch(regex_pattern, output)
        logging.debug("regex match: %s", regex_match)

        if regex_match:
            slurm_duration = regex_match.group(3).strip()
            duration = parse_slurm_duration(slurm_duration)
            submitted_time = calculate_timedelta_offset_from_now(duration)
            
            status = regex_match.group(4).strip()
            logging.debug("extracted status: %s", status)
            if "CANCELLED by" in status:
                status = status[:9]
                logging.debug("detected cancelled by, extracted status: %s", status)
            
            comment = regex_match.group(5).strip()

            return RecoveredSlurmData(submitted_time, status, comment)

        if allow_none:
            logging.debug("returning None (allowed)")
            return None

        logging.debug("regex match is None and None is not allowed, raising OSError")
        raise OSError(
            f"sacct command has unexpected output \nexpected:\n{regex_match}\ngot:\n{output}"
        )

@dataclass
class RecoveredSlurmData:
    submitted_time: datetime.datetime
    status: str
    comment: str
