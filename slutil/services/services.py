from datetime import datetime
from slutil.model.Record import Record
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.services.abstract_uow import AbstractUnitOfWork
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
        datetime.strftime(job.submitted_timestamp, "%Y-%m-%d %H:%M:%S"),
        job.git_tag,
        job.sbatch,
        job.status,
        job.description,
    )


def get_job(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, slurm_id: int
) -> JobDTO:
    with uow:
        job = uow.jobs.get(slurm_id)
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        if job.status not in end_states:
            job.status = slurm_service.get_job_status(job.slurm_id)
        uow.commit()
        return map_job_to_jobDTO(job)


def delete_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get(slurm_id)
        job.deleted = True
        uow.commit()


def undelete_job(uow: AbstractUnitOfWork, slurm_id: int):
    with uow:
        job = uow.jobs.get_deleted(slurm_id)
        job.deleted = False
        uow.commit()


def report(
    slurm_service: AbstractSlurmService, uow: AbstractUnitOfWork, count: int
) -> list[JobDTO]:
    with uow:
        all_jobs = uow.jobs.list()
        output = sorted([j for j in all_jobs if not j.deleted])[:count]
        end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
        for job in output:
            if job.status not in end_states:
                job.status = slurm_service.get_job_status(job.slurm_id)
        uow.commit()
        return [map_job_to_jobDTO(j) for j in output]


def submit(
    slurm_service: AbstractSlurmService,
    uow: AbstractUnitOfWork,
    vcs: AbstractVCS,
    req: JobRequestDTO,
) -> str:
    with uow:
        repo_stamp = vcs.get_current_commit()
        timestamp = datetime.now()
        slurm_id = slurm_service.submit_job(req.sbatch)

        new_job = Record(
            slurm_id, timestamp, repo_stamp, req.sbatch, "PENDING", req.description
        )
        uow.jobs.add(new_job)
        uow.commit()

        return str(slurm_id)

def update_description(uow: AbstractUnitOfWork, slurm_id: int, new_description: str):
    with uow:
        j = uow.jobs.get(slurm_id)
        j.description = new_description
        # print(j.description)
        uow.commit()