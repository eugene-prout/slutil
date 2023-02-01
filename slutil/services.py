import subprocess
import re
from datetime import datetime
from slutil.Record import Record
from slutil.slurm import get_job_status, submit_job
from dataclasses import dataclass

@dataclass
class JobDTO:
    slurm_id: int
    submitted_timestamp: str
    git_tag: str
    sbatch: str
    status: str
    description: str

@dataclass
class JobRequestDTO:
    sbatch: str
    description: str

def map_job_to_jobDTO(job: Record) -> JobDTO:
    return JobDTO(
        job.slurm_id,
        datetime.strftime(job.submitted_timestamp, '%Y-%m-%d %H:%M:%S'),
        job.git_tag,
        job.sbatch,
        job.status,
        job.description
    )



def get_job(slurm_id: int, uow) -> JobDTO:
    with uow:
        job = uow.jobs.get(slurm_id)
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        if job.status not in end_states:
            job.status = get_job_status(job.slurm_id)
        uow.commit()
        return map_job_to_jobDTO(job)

def report(uow, count: int) -> list[JobDTO]:
    with uow:
        all_jobs = uow.jobs.list()
        output = sorted(all_jobs)[:count]
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        for job in output:
            if job.status not in end_states:            
                job.status = get_job_status(job.slurm_id)
        uow.commit()
        return [map_job_to_jobDTO(j) for j in output]

def submit(req: JobRequestDTO, uow) -> str:
    with uow:
        repo_stamp =  subprocess.check_output(["git", "describe", "--always"]).strip().decode()
        timestamp = datetime.now()
        slurm_id = submit_job(req.sbatch)

        new_job = Record(slurm_id, timestamp, repo_stamp, req.sbatch, "PENDING", req.description)
        uow.jobs.add(new_job)
        uow.commit()

        return str(slurm_id)
