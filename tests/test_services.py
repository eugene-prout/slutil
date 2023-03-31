from slutil.model.Record import Record, JobStatus
from slutil.services.services import (
    get_job,
    recent,
    filter_jobs,
    FilterQuery,
)
from slutil.services.dto import JobDTO, map_job_to_jobDTO
from datetime import datetime
import re


def test_get_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(123456, time, "cae42f", "test.sbatch", JobStatus["PENDING"], "testing get job", time)

    expected_output = JobDTO(
        123456,
        datetime.strftime(time, "%y-%m-%d %H:%M:%S"),
        "cae42f",
        "test.sbatch",
        "COMPLETED",
        "testing get job",
        "NONE",
        "NONE",
        ["NONE"]
    )

    in_memory_uow.jobs.add(job)

    output = get_job(fake_slurm, in_memory_uow, job.slurm_id)

    assert output.job == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]


def test_report_updates_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(123456, time, "cae42f", "test.sbatch", JobStatus.PENDING, "testing get job", time)

    expected_output = [
        JobDTO(
            123456,
            datetime.strftime(time, "%y-%m-%d %H:%M:%S"),
            "cae42f",
            "test.sbatch",
            "COMPLETED",
            "testing get job",
            "NONE",
            "NONE",
            ["NONE"]
        )
    ]

    in_memory_uow.jobs.add(job)

    output = recent(fake_slurm, in_memory_uow, 10)

    assert output.jobs == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]


def test_search_description_no_match(in_memory_uow, fake_slurm):
    output = filter_jobs(
        in_memory_uow, fake_slurm, FilterQuery(status_filter=re.compile("COMPLETED"))
    )

    assert output.jobs == []


def test_search_description_some_match(in_memory_uow, fake_slurm):
    time = datetime.now()
    job1 = Record(
        123456, time, "cae42f", "test.sbatch", JobStatus.PENDING, "testing, description", time
    )
    job2 = Record(123457, time, "cae42f", "test.sbatch", JobStatus.PENDING, "script", time)
    job3 = Record(123458, time, "cae42f", "test.sbatch", JobStatus.PENDING, "test", time)

    in_memory_uow.jobs.add(job1)
    in_memory_uow.jobs.add(job2)
    in_memory_uow.jobs.add(job3)

    output = filter_jobs(
        in_memory_uow, fake_slurm, FilterQuery(description_filter=re.compile("script"))
    )

    assert all(x in [map_job_to_jobDTO(job1), map_job_to_jobDTO(job2)] for x in output.jobs)
