from click.testing import CliRunner
from slutil.main import command_factory
from slutil.CsvUow import CsvUnitOfWork
from slutil.fake_slurm import FakeSlurm
import re 
import os
from datetime import datetime


def test_submit_job():
    runner = CliRunner()
    with runner.isolated_filesystem():

        with open('test.sbatch', 'w') as f:
            f.write('srun ...')

        cmd = command_factory(CsvUnitOfWork(""), FakeSlurm())

        result = runner.invoke(cmd, ['submit', 'test.sbatch', 'test description'])
        assert result.exit_code == 0

        file_contents = ""
        with open(".slutil_job_history.csv", "r") as f:
            file_contents = f.read()
      
        assert re.match(r"^Successfully submitted job (\d+)$", result.output)
        job_number = re.match(r"^Successfully submitted job (\d+)$", result.output).group(1)

        git_hash_regex = r".*"
        date_match = rf"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')}:\d\d"
        file_contents_expected = rf"{job_number},{date_match},{git_hash_regex},test.sbatch,PENDING,test description"

        assert re.match(file_contents_expected, file_contents)