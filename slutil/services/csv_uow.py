import os
from slutil.adapters.csv_repository import CsvRepository
from slutil.services.abstract_uow import AbstractUnitOfWork
import csv


class CsvUnitOfWork(AbstractUnitOfWork):
    jobs: CsvRepository

    def __init__(self, folder: str):
        self.jobs = CsvRepository(folder)

    def serialise_job(self, job):
        dependency_name = job.dependencies.type.name if job.dependencies else "none"
        dependency_state = job.dependencies.state.name if job.dependencies else "none"
        dependency_ids = job.dependencies.ids if job.dependencies else []
        return [
            job.slurm_id,
            job.submitted_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            job.git_tag,
            job.sbatch,
            job.status.name,
            job.description,
            dependency_name,
            dependency_state,
            dependency_ids,
            job.deleted,
        ]

    def _commit(self):
        temp_path = os.path.join(
            os.path.dirname(self.jobs.csv_path), ".slutil_temp.csv"
        )
        try:
            data = [self.serialise_job(j) for j in self.jobs.list_all()]
            with open(temp_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(data)

            os.replace(temp_path, self.jobs.csv_path)
        except Exception as e:
            os.remove(temp_path)
            raise e

    def rollback(self):
        pass
