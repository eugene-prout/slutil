from datetime import datetime
import json
from multiprocessing import Value
from slutil.model.Record import JobStatus, Record

def datetime_formatter(d: datetime):
    return d.isoformat()

def serialise_record_to_json(job: Record) -> str:
    dependency_name = job.dependencies.type.name if job.dependencies else "none"
    dependency_state = job.dependencies.state.name if job.dependencies else "none"
    dependency_ids = job.dependencies.ids if job.dependencies else []

    data = {
        "submitted_timestamp": job.submitted_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "git_tag": job.git_tag,
        "sbatch": job.sbatch,
        "description": job.description,
        "dependency_name": dependency_name,
        "depedency_state": dependency_state,
        "depedency_ids": dependency_ids
    }
    metadata = {
        "slutil_record": "yes",
        "data": data
    }
    
    return json.dumps(metadata)

def load_record_from_json(json_string: str) -> Record:
    parsed_json = json.loads(json_string)
    if parsed_json.get("slutil_record", None) != "yes":
        raise ValueError("Tried to load record from incorrectly formatted json")
    
    job_data = parsed_json["data"]
    record = Record(
            int(job_data["job_id"]),
            datetime.strptime(job_data["submitted_timestamp"], "%Y-%m-%d %H:%M:%S"),
            job_data["git_tag"],
            job_data["sbatch"],
            JobStatus[job_data["status"]],
            job_data["description"],
            datetime.strptime(job_data["last_updated"], "%Y-%m-%d %H:%M:%S")
        )
    return record