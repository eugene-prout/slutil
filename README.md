# slutil

A command line utility to view Slurm jobs.


```
Usage: slutil [OPTIONS] COMMAND [ARGS]...

Commands:
  report  Get status of multiple jobs
  status  Get status of a slurm job.
  submit  Submit a slurm job.
```

## Contributing

Pushes to `main` are forbidden, all changes must go through a PR before merging. All tests must pass for a PR to be merged. Code is to be formatted with `black`. Built with poetry.

## submit

Add metadata to an `sbatch` command and store data in the database

**Must** be used to log jobs in the database.

```
Usage: slutil submit [OPTIONS] SBATCH_FILE DESCRIPTION

  Submit a slurm job.

  SBATCH_FILE is a path to the .sbatch file for the job

  DESCRIPTION is a text field describing the job

Options:
  --help  Show this message and exit.
```

## report

View list of recent jobs

- Count parameter specifies the number of jobs to be displayed. Defaults to 10.
- Truncated to screen width by default, `-v` to enable word-wrap.

```
Usage: slutil report [OPTIONS]

  Get status of multiple jobs

Options:
  -c, --count INTEGER
  -v, --verbose
  --help               Show this message and exit.
```

## status

Displays the data on a specific job

```
Usage: slutil status [OPTIONS] SLURM_ID

  Get status of a slurm job.

  SLURM_ID is the id of the job to check.

Options:
  --help  Show this message and exit.
```