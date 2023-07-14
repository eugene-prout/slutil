from __future__ import annotations

from pathlib import Path
import csv
import ast
from typing import Optional

from marshmallow import Schema, fields, validate
from slutil.adapters.abstract_repository import AbstractRepository
from slutil.model.Record import Record, Dependencies, DependencyType, JobStatus, DependencyState
from datetime import datetime

class CSVFormatError(Exception):
    pass


file_entry = {
    "job_id": fields.Integer(),
    "submitted_timestamp": fields.DateTime("%Y-%m-%d %H:%M:%S"),
    "git_tag": fields.String(),
    "sbatch": fields.String(),
    "status": fields.Enum(JobStatus),
    "description": fields.String(),
    "last_updated": fields.DateTime("%Y-%m-%d %H:%M:%S"),
    "dependency_type": fields.Enum(DependencyType, allow_none=True),
    "dependency_state": fields.Enum(DependencyState, allow_none=True),
    "dependency_ids": fields.String(validate=validate.Regexp(r"\[[^\]]*\]")),
    "is_deleted": fields.Boolean()
}

file_entry_schema = Schema.from_dict(file_entry)

class CsvRepository(AbstractRepository):
    def __init__(self, csv_path: Optional[Path]=None):
        self._jobs: list[Record] = []
        
        if csv_path:
            self.csv_path = csv_path
        else:
            self.csv_path = self.find_file()
        
        if self.csv_path:
            self._load()

    @staticmethod
    def create_file():
        open(".slutil_job_history.csv", "a+").close() 

    @staticmethod
    def find_file() -> Optional[Path]:
        filename = ".slutil_job_history.csv"
        file_path = Path.cwd() / filename

        if file_path.exists():
            return file_path

        for directory in Path.cwd().parents:
            file_path = directory / filename
            if file_path.exists():
                return file_path
            
        return None 

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
        if self.csv_path is None:
            raise ValueError("csv_repository attempting to load from csv_path=None")
        
        with open(self.csv_path, mode="r") as csvfile:
            reader = csv.DictReader(csvfile, list(file_entry.keys()), restval="error", restkey="error")
            for line_num, line in enumerate(reader, 1):
                if line["dependency_state"] == "none":
                    line["dependency_state"] = None
                if line["dependency_type"] == "none":
                    line["dependency_type"] = None
                
                if "error" in line.keys() or "error" in line.values():
                    raise CSVFormatError(f"CSV format error: line number {line_num} is of an incorrect length, please fix the csv before trying again")
                
                errors = file_entry_schema().validate(line)
                if errors:
                    error_fmt = "\n".join("{} {}".format(k, v) for k, v in errors.items())
                    raise CSVFormatError(f"CSV record has errors, line {line_num}: {error_fmt}")

                dependency = None
                if line["dependency_type"] != None and line["dependency_state"] != None:
                    dependency = Dependencies(DependencyType[line["dependency_type"]], DependencyState[line["dependency_state"]], [int(i) for i in ast.literal_eval(line["dependency_ids"])])
                
                record = Record(
                    int(line["job_id"]),
                    datetime.strptime(line["submitted_timestamp"], "%Y-%m-%d %H:%M:%S"),
                    line["git_tag"],
                    line["sbatch"],
                    JobStatus[line["status"]],
                    line["description"],
                    datetime.strptime(line["last_updated"], "%Y-%m-%d %H:%M:%S"),
                    dependency,
                    deleted=line["is_deleted"] == "True",
                )
                self._jobs.append(record)

    def list(self) -> list[Record]:
        return [j for j in self._jobs if not j.deleted]

    def list_all(self):
        return [j for j in self._jobs]
