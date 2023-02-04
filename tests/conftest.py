import pytest
from slutil.Record import Record
from slutil.fake_slurm import FakeSlurm

class FakeRepository():
    def __init__(self):
        self._jobs = []

    def get(self, job_id):
        try:
            return next(x for x in self._jobs if x.slurm_id == job_id)
        except StopIteration:
            raise KeyError("No job exists with specified id")

    def add(self, job):
        self._jobs.append(job)

    def list(self) -> list[Record]:
        return list(self._jobs)

class FakeUow():
    def __init__(self):
        self.jobs = FakeRepository()
        self.commited = False

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def commit(self):
        self.commited = True

    def rollback(self):
        pass


@pytest.fixture
def in_memory_repository():
    return FakeRepository()

@pytest.fixture
def in_memory_uow():
    return FakeUow()

@pytest.fixture
def fake_slurm():
    return FakeSlurm()