from slutil.model.Record import Record
from slutil.services.services import JobDTO, get_job, report, search_description
from datetime import datetime


def test_get_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(123456, time, "cae42f", "test.sbatch", "PENDING", "testing get job")

    expected_output = JobDTO(
        123456,
        datetime.strftime(time, "%Y-%m-%d %H:%M:%S"),
        "cae42f",
        "test.sbatch",
        "COMPLETED",
        "testing get job",
    )

    in_memory_uow.jobs.add(job)

    output = get_job(fake_slurm, in_memory_uow, job.slurm_id)

    assert output == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]


def test_report_updates_job(in_memory_uow, fake_slurm):
    time = datetime.now()
    job = Record(123456, time, "cae42f", "test.sbatch", "PENDING", "testing get job")

    expected_output = [
        JobDTO(
            123456,
            datetime.strftime(time, "%Y-%m-%d %H:%M:%S"),
            "cae42f",
            "test.sbatch",
            "COMPLETED",
            "testing get job",
        )
    ]

    in_memory_uow.jobs.add(job)

    output = report(fake_slurm, in_memory_uow, 10)

    assert output == expected_output
    assert in_memory_uow.commited == True
    assert in_memory_uow.jobs._jobs == [job]

def test_search_description_no_match(in_memory_uow, fake_slurm):
    output = search_description(in_memory_uow, fake_slurm, "testing")
    
    assert output == []

def test_search_description_some_match(in_memory_uow, fake_slurm):
    time = datetime.now()
    job1 = Record(123456, time, "cae42f", "test.sbatch", "PENDING", "testing, description")
    job2 = Record(123457, time, "cae42f", "test.sbatch", "PENDING", "script")
    job3 = Record(123458, time, "cae42f", "test.sbatch", "PENDING", "test")
    
    in_memory_uow.jobs.add(job1)
    in_memory_uow.jobs.add(job2)
    in_memory_uow.jobs.add(job3)

    output = search_description(in_memory_uow, fake_slurm, "script")

    assert output == [job1, job2]
