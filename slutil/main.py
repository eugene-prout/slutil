from pathlib import Path
import subprocess
import csv
import click
import re
from datetime import datetime
from rich.console import Console
from rich.table import Table           
from dataclasses import dataclass
from rich.text import Text
from functools import total_ordering
from rich import box
import os

def get_git_short_hash():
    return subprocess.check_output(["git", "describe", "--always"]).strip().decode()


CSV_PATH = ".slutil_job_history.csv"

@click.group()
def cli():
    pass

def job_status(job_id: int):
    """
    sacct -j {jobid}
    """
    """
            JobID    JobName  Partition    Account  AllocCPUS      State ExitCode
    ------------ ---------- ---------- ---------- ---------- ---------- --------
    607582       slurm-test  cpu-batch         ug          1  COMPLETED      0:0
    607582.batch      batch                    ug          1  COMPLETED      0:0
    """
    regex_pattern = r"^(\s*JobID\s*JobName\s*Partition\s*Account\s*AllocCPUS\s*State\s*ExitCode\s*)(-*\s*){7}(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*)(\S*\s*){7}$"
    output = subprocess.check_output(["sacct", "-j", str(job_id)]).strip().decode()
    regex_match = re.match(regex_pattern, output)
    
    return regex_match.group(8).strip()

"""
Slurm job codes
COMPLETED	CD	The job has completed successfully.
COMPLETING	CG	The job is finishing but some processes are still active.
FAILED	F	The job terminated with a non-zero exit code and failed to execute.
PENDING	PD	The job is waiting for resource allocation. It will eventually run.
PREEMPTED	PR	The job was terminated because of preemption by another job.
RUNNING	R	The job currently is allocated to a node and is running.
SUSPENDED	S	A running job has been stopped with its cores released to other jobs.
STOPPED	ST	A running job has been stopped with its cores retained.
"""

@dataclass
@total_ordering
class Record():
    slurm_id: int
    submitted_timestamp: datetime
    git_tag: str
    sbatch: str
    status: str
    description: str

    def __eq__(self, other):
        return self.slurm_id == other.slurm_id

    def __gt__(self, other):
        return self.slurm_id > other.slurm_id

    def to_row(self) -> list:
        # slurm_id, submitted timestamp, git tag, sbatch, status, description
        return [self.slurm_id, self.submitted_timestamp.strftime('%Y-%m-%d %H:%M:%S'), self.git_tag, self.sbatch, self.status, self.description]

    def to_rich_text(self, verbose: bool) -> list:
        status_color_map = {
            "COMPLETED": "green3",
            "COMPLETING": "chartreuse3",
            "FAILED": "red3",
            "PENDING": "blue3",
            "PREEMPTED": "red3",
            "RUNNING": "yellow3",
            "SUSPENDED": "orange3",
            "STOPPED": "red3"
        }
        goal_color = status_color_map[self.status]
        if verbose:
            description = self.description
        else:
            description = Text(self.description, overflow="ellipsis", no_wrap=True)
        return [str(self.slurm_id), f"[{goal_color}]{self.status}[/{goal_color}]", description, self.submitted_timestamp.strftime('%y-%m-%d %H:%M'), self.git_tag, self.sbatch]

def create_record_from_line(line: list[str]):
    # this should be in a repository
    formatted_line = [val.strip() for val in line]
    return Record(
        int(formatted_line[0]),
        datetime.strptime(formatted_line[1], '%Y-%m-%d %H:%M:%S'), 
        formatted_line[2], 
        formatted_line[3], 
        formatted_line[4], 
        formatted_line[5])

def read_csv():
    all_jobs = []
    with open(CSV_PATH, mode='r') as csvfile:
        all_jobs = [create_record_from_line(line) for line in csv.reader(csvfile)]
    return all_jobs
    
def write_csv(jobs: list[Record]):
    with open(CSV_PATH, mode='w', newline='') as csvfile:
        # CSV Layout:  
        # slurm_id, submitted timestamp, git tag, sbatch, status, description
        csv.writer(csvfile).writerows([j.to_row() for j in jobs])


@cli.command()
@click.argument('slurm_id', type=int, )
def status(slurm_id: int):
    """Get status of a slurm job.

    SLURM_ID is the id of the job to check.
    """
    all_jobs = read_csv()
    job = None
    try:
        job = next(x for x in all_jobs if x.slurm_id == slurm_id)
    except StopIteration:
        console = Console()
        console.print("[red]Error: Job not found in database[/red]")
        exit(1)
    end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
    if job.status not in end_states:
        # pass
        job.status = job_status(job.slurm_id)

    write_csv(all_jobs)

    table = Table(
        title=f"Job {slurm_id}", 
        box=box.ROUNDED,
        expand=True)
    
    # slurm_id, submitted timestamp, git tag, sbatch, status, description
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Submit Time")
    table.add_column("Commit")
    table.add_column("sbatch File")

    table.add_row(*job.to_rich_text(True))

    console = Console()
    console.print(table, overflow="ellipsis")    

@cli.command()
@click.option("-c", "--count", default=10)
@click.option("-v", "--verbose", is_flag=True, default=False)
def report(count: int, verbose: bool):
    """Get status of multiple jobs
    """
    all_jobs = read_csv()
    all_jobs.sort(reverse=True)
    
    end_states = ["COMPLETED", "FAILED", "PREEMPTED"]
    for job in all_jobs:
        if job.status not in end_states:
            # pass
            job.status = job_status(job.slurm_id)

    write_csv(all_jobs)
  
    table = Table(
        title="Slurm job status", 
        caption=f"Showing last {count} jobs", 
        expand=True)
    
    # slurm_id, submitted timestamp, git tag, sbatch, status, description
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Description")
    table.add_column("Submit Time")
    table.add_column("Commit")
    table.add_column("sbatch File")
    
    for j in all_jobs[:count]:
        table.add_row(*j.to_rich_text(verbose))
    if len(all_jobs) == 0:
        table.caption = "(No jobs found)"

    console = Console()
    console.print(table, overflow="ellipsis")    


@cli.command()
@click.argument('sbatch_file', type=click.Path(exists=True))
@click.argument('description', type=str)
def submit(sbatch_file: str, description: str):
    """Submit a slurm job. 
    
    SBATCH_FILE is a path to the .sbatch file for the job
    
    DESCRIPTION is a text field describing the job
    """
    repo_stamp = get_git_short_hash()
    timestamp = datetime.now()

    proc = subprocess.run(f'sbatch {sbatch_file}', check=True, capture_output=True, shell=True)
    
    # proc.stdout should be "Submitted batch job XXXXXX"
    regex_match = re.match(r"^(Submitted batch job )(\d*)$", proc.stdout.decode("utf-8"))
    slurm_id = regex_match.group(2)
    new_job = Record(slurm_id, timestamp, repo_stamp, sbatch_file, "PENDING", description)
    with open(CSV_PATH, mode='a') as csvfile:
        csv.writer(csvfile).writerow(new_job.to_row())

    click.echo(f"Successfully submitted job {slurm_id}")

def start_cli():
    global CSV_PATH
    try:
        try:
            subprocess.run(["sinfo"], capture_output=True, check=True)
        except FileNotFoundError:
            raise click.UsageError("Slurm accessed required but cannot access Slurm")
        f = open(CSV_PATH, 'a+')
        f.close()
        cli()
    except Exception as e:
        raise e
        # console = Console()
        # console.print(f"[red]Error: {str(e)}[/red]")

if __name__ == '__main__':
    start_cli()
