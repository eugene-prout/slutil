from slutil.Record import Record
from hypothesis import given
from hypothesis import strategies
from slutil.services import JobDTO, get_job, map_job_to_jobDTO, report
from datetime import datetime
from unittest.mock import patch
# @given(sample=strategies.from_type(Record)) 

def test_get_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(
        123456,
        time,
        "cae42f",
        "test.sbatch",
        "PENDING",
        "testing get job"
    )

    expected_output = JobDTO(
        123456,
        datetime.strftime(time, '%Y-%m-%d %H:%M:%S'),
        "cae42f",
        "test.sbatch",
        "COMPLETED",
        "testing get job"
    )

    in_memory_uow.jobs.add(job)

    output = get_job(fake_slurm, in_memory_uow, job.slurm_id)

    assert output == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]

def test_report_updates_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(
        123456,
        time,
        "cae42f",
        "test.sbatch",
        "PENDING",
        "testing get job"
    )

    expected_output = [JobDTO(
        123456,
        datetime.strftime(time, '%Y-%m-%d %H:%M:%S'),
        "cae42f",
        "test.sbatch",
        "COMPLETED",
        "testing get job"
    )]

    in_memory_uow.jobs.add(job)

    output = report(fake_slurm, in_memory_uow, 10)

    assert output == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]