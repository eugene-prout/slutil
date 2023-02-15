import pytest
from slutil.model.Record import Record
from slutil.adapters.abstract_repository import AbstractRepository
from slutil.adapters.abstract_vcs import AbstractVCS
from slutil.adapters.abstract_slurm_service import AbstractSlurmService
from slutil.services.abstract_uow import AbstractUnitOfWork
import random


class FakeRepository(AbstractRepository):
    def __init__(self):
        self._jobs: list[Record] = []

    def get(self, job_id):
        try:
            return next(x for x in self._jobs if x.slurm_id == job_id and not x.deleted)
        except StopIteration:
            raise KeyError("No job exists with specified id")

    def get_deleted(self, job_id):
        try:
            return next(x for x in self._jobs if x.slurm_id == job_id and x.deleted)
        except StopIteration:
            raise KeyError("No job exists with specified id")

    def add(self, job):
        self._jobs.append(job)

    def list(self) -> list[Record]:
        return [j for j in self._jobs if not j.deleted]

    def list_all(self):
        return list(self._jobs)


class FakeUow(AbstractUnitOfWork):
    def __init__(self):
        self.jobs = FakeRepository()
        self.commited = False

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def _commit(self):
        self.commited = True

    def rollback(self):
        pass


class FakeSlurm(AbstractSlurmService):
    @staticmethod
    def get_job_status(job_id: int):
        return "COMPLETED"

    @staticmethod
    def submit_job(sbatch: str, dependency, depenency_list) -> int:
        return random.randrange(100000, 999999)

    @staticmethod
    def test_slurm_accessible():
        return True


class FakeVCS(AbstractVCS):
    @staticmethod
    def get_current_commit():
        return "abc123"


@pytest.fixture
def in_memory_repository():
    return FakeRepository()


@pytest.fixture
def in_memory_uow():
    return FakeUow()


@pytest.fixture
def fake_slurm():
    return FakeSlurm()


@pytest.fixture
def fake_vcs():
    return FakeVCS()
