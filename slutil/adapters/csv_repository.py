from pathlib import Path
import csv
from slutil.adapters.abstract_repository import AbstractRepository
from slutil.model.Record import Record
from datetime import datetime


class CsvRepository(AbstractRepository):
    def __init__(self, folder: str):
        self.csv_path = Path(folder) / ".slutil_job_history.csv"
        f = open(self.csv_path, "a+")
        f.close()
        self._jobs: list[Record] = []
        self._load()

    def get(self, job_id: int) -> Record:
        try:
            return next(x for x in self._jobs if x.slurm_id == job_id and not x.deleted)
        except StopIteration:
            raise KeyError("No job exists with specified id")

    def get_deleted(self, job_id: int) -> Record:
        try:
            return next(x for x in self._jobs if x.slurm_id == job_id and x.deleted)
        except StopIteration:
            raise KeyError("No job has been deleted with the specified id")

    def add(self, job: Record):
        self._jobs.append(job)

    def _load(self):
        with open(self.csv_path, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                formatted_line = [val.strip() for val in line]
                record = Record(
                    int(formatted_line[0]),
                    datetime.strptime(formatted_line[1], "%Y-%m-%d %H:%M:%S"),
                    formatted_line[2],
                    formatted_line[3],
                    formatted_line[4],
                    formatted_line[5],
                    formatted_line[6] == "True",
                )
                self._jobs.append(record)

    def list(self) -> list[Record]:
        return [j for j in self._jobs if not j.deleted]

    def list_all(self):
        return [j for j in self._jobs]
