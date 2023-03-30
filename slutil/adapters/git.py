import logging
from slutil.adapters.abstract_vcs import AbstractVCS
import subprocess


class Git(AbstractVCS):
    @staticmethod
    def get_current_commit():
        try:
            output = (
                subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.STDOUT)
                .strip()
                .decode()
            )

            status = (
                subprocess.check_output(["git", "status", "--porcelain"])
                .decode()
            )

            # slutil writes to two files (.slutil_job_hisotry.csv and debug.log) 
            # they show up as updated or untracked so we allow them to be changed
            if status.count("\n") > 2:
                logging.debug("git directory dirty, adding [d] to commit tag")
                output += "[d]"

            return output
        except subprocess.CalledProcessError as e:
            logging.debug("error running %s, stderr: %s, stdout: %s", e.cmd, e.stderr, e.stdout)
            return "UNKNOWN"