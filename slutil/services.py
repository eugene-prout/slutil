import subprocess
import re
from datetime import datetime
from slutil.Record import Record
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

def get_job_status_from_slurm(job_id: int):
    regex_pattern = r"^(\s*JobID\s*JobName\s*Partition\s*Account\s*AllocCPUS\s*State\s*ExitCode\s*)(-*\s*){7}(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*){7}$"
    output = subprocess.check_output(["sacct", "-j", str(job_id)]).strip().decode()
    regex_match = re.match(regex_pattern, output)
    
    return regex_match.group(8).strip()

def get_job_status(slurm_id: int, uow) -> JobDTO:
    with uow:
        job = uow.jobs.get(slurm_id)
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        if job.status not in end_states:
            job.status = get_job_status_from_slurm(job.slurm_id)
        uow.commit()
        return map_job_to_jobDTO(job)

def report(uow, count: int) -> list[JobDTO]:
    with uow:
        all_jobs = uow.jobs.list()
        output = sorted(all_jobs)[:count]
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        for job in output:
            if job.status not in end_states:            
                job.status = get_job_status_from_slurm(job.slurm_id)
        uow.commit()
        return [map_job_to_jobDTO(j) for j in output]

def submit(req: JobRequestDTO, uow) -> str:
    with uow:
        repo_stamp =  subprocess.check_output(["git", "describe", "--always"]).strip().decode()
        timestamp = datetime.now()
        proc = subprocess.run(f'sbatch {req.sbatch}', check=True, capture_output=True, shell=True)        
        # proc.stdout should be "Submitted batch job XXXXXX"
        regex_match = re.match(r"^(Submitted batch job )(\d*)$", proc.stdout.decode("utf-8"))
        slurm_id = regex_match.group(2)
        new_job = Record(slurm_id, timestamp, repo_stamp, req.sbatch, "PENDING", req.description)
        uow.jobs.add(new_job)
        return str(slurm_id)

def test_slurm_accessible():
    try: 
        subprocess.run(["sinfo"], capture_output=True, check=True)
        return True
    except:
        return False

