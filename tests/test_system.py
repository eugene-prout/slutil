from click.testing import CliRunner
from slutil.main import command_factory
from slutil.services.csv_uow import CsvUnitOfWork
import re
from datetime import datetime


def test_submit_job(fake_slurm):
    runner = CliRunner()
    with runner.isolated_filesystem():

        with open('test.sbatch', 'w') as f:
            f.write('srun ...')

        cmd = command_factory(CsvUnitOfWork(""), fake_slurm)

        result = runner.invoke(cmd, ['submit', 'test.sbatch', 'test description'])
        assert result.exit_code == 0

        file_contents = ""
        with open(".slutil_job_history.csv", "r") as f:
            file_contents = f.read()
      
        assert re.match(r"^Successfully submitted job (\d+)$", result.output)
        job_number = re.match(r"^Successfully submitted job (\d+)$", result.output).group(1) #type: ignore

        git_hash_regex = r".*"
        date_match = rf"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')}:\d\d"
        file_contents_expected = rf"{job_number},{date_match},{git_hash_regex},test.sbatch,PENDING,test description"

        assert re.match(file_contents_expected, file_contents)

def test_status_job(fake_slurm):
    runner = CliRunner()
    with runner.isolated_filesystem():
        original_file_contents = "329981,2023-02-04 13:39:39,dddbffe,fake.sbatch,COMPLETED,test\n"
        with open('.slutil_job_history.csv', 'w') as f:
            f.write(original_file_contents)

        cmd = command_factory(CsvUnitOfWork(""), fake_slurm)

        result = runner.invoke(cmd, ['status', '329981'])
        assert result.exit_code == 0

        file_contents = ""
        with open(".slutil_job_history.csv", "r") as f:
            file_contents = f.read()
      
        assert file_contents == original_file_contents

        # CliRunner.invoke does not respect terminal size, (https://github.com/pallets/click/issues/1997) 
        # Accept truncated output here until fixed
        job_details = ["329981","2023-02-04","dddbffe","fake.sbatch","COMPLETED","test"]
        print(result.output)
        for d in job_details:
            assert d in result.output

def test_status_job_non_existant(fake_slurm):
    runner = CliRunner()
    with runner.isolated_filesystem():
        original_file_contents = "329981,2023-02-04 13:39:39,dddbffe,fake.sbatch,COMPLETED,test\n"
        with open('.slutil_job_history.csv', 'w') as f:
            f.write(original_file_contents)

        cmd = command_factory(CsvUnitOfWork(""), fake_slurm)

        result = runner.invoke(cmd, ['status', '123456'])
        assert result.exit_code == 1

        file_contents = ""
        with open(".slutil_job_history.csv", "r") as f:
            file_contents = f.read()
      
        assert file_contents == original_file_contents

        assert isinstance(result.exception, KeyError)
        assert str(result.exception) == "'No job exists with specified id'"

def test_report(fake_slurm):
    runner = CliRunner()
    with runner.isolated_filesystem():
        original_file_contents = "594334,2023-02-04 13:32:47,dddbffe,fake.sbatch,COMPLETED,test\n329981,2023-02-04 13:39:39,dddbffe,fake2.sbatch,COMPLETED,test2\n"
        with open('.slutil_job_history.csv', 'w') as f:
            f.write(original_file_contents)

        cmd = command_factory(CsvUnitOfWork(""), fake_slurm)

        result = runner.invoke(cmd, ['report'])
        assert result.exit_code == 0

        file_contents = ""
        with open(".slutil_job_history.csv", "r") as f:
            file_contents = f.read()
      
        assert file_contents == original_file_contents

        # CliRunner.invoke does not respect terminal size (https://github.com/pallets/click/issues/1997) 
        # Accept truncated output here until fixed
        job_details = [
            ["329981","2023-02-04","dddbffe","fake.sbatch","COMPLETED","test"],
            ["594334","2023-02-04","dddbffe","fake2.sbatch","COMPLETED", "test2"]
        ]
        
        for j in job_details:
            for d in j:
                assert d in result.output

def test_report_no_jobs(fake_slurm):
    runner = CliRunner()
    with runner.isolated_filesystem():
        cmd = command_factory(CsvUnitOfWork(""), fake_slurm)

        result = runner.invoke(cmd, ['report'])
        assert result.exit_code == 0
      
        assert "(No jobs found)" in result.output