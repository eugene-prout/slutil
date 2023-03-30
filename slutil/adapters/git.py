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
            return output
        except subprocess.CalledProcessError:
            return "UNKNOWN"