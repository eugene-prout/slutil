from slutil.CsvRepository import CsvRepository
import csv


class CsvUnitOfWork():
    def __init__(self, folder):
        self.jobs = CsvRepository(folder)

    def __enter__(self):
        pass

    def __exit__(self, *args):
        pass

    def commit(self):
        with self.jobs._csv_path.open("w") as f:
            writer = csv.writer(f)
            # writer.writerow(["slurm_id", "submit_time", "repo_commit_tag",
                            # "sbatch_file", "status", "description"])
            for job in self.jobs.list():
                writer.writerow(
                    [job.slurm_id,
                     job.submitted_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                     job.git_tag,
                     job.sbatch,
                     job.status,
                     job.description]
                )

    def rollback(self):
        pass
