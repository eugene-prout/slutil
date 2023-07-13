from pathlib import Path
from slutil.adapters.csv_repository import CsvRepository
import click
import logging

def cmd_init():
    """Initalise a slutil data file in the current directory
    """
    logging.debug("cli: init file requested")
    
    repo_location = CsvRepository.find_file()
    if repo_location is None:
        CsvRepository.create_file()
        click.echo("slutil datafile created successfully")
    else:
        repo_folder = repo_location.parent
        if repo_folder == Path.cwd():
            raise FileExistsError("A slutil datafile exists in the current directory, please remove that file before creating another")
        else:
            if click.confirm('A slutil datafile exists in a parent directory. Would you like to create another in the current folder?'):
                CsvRepository.create_file()
                click.echo("slutil datafile created successfully")
