import os
from pathlib import Path
from typing import Optional
from slutil.adapters.csv_repository import CsvRepository
from slutil.model.Record import Record
from slutil.services.abstract_uow import AbstractUnitOfWork
import csv


class CsvUnitOfWork(AbstractUnitOfWork):
    jobs: CsvRepository

    def __init__(self, csv_path: Optional[Path]=None):
        self.jobs = CsvRepository(csv_path)

    def __enter__(self):
        if self.jobs.csv_path:
            return self
        else:
            raise FileNotFoundError("No .slutil_job_history.csv file found in current directory or parents. Please use 'slutil init' to create the file")

    def serialise_job(self, job: Record):
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
            job.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
            dependency_name,
            dependency_state,
            dependency_ids,
            job.deleted,
        ]

    def _commit(self):
        if self.jobs.csv_path is None:
            raise ValueError("csv_repository attempting to load from csv_path=None")
        
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
