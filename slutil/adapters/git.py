from slutil.adapters.abstract_vcs import AbstractVCS
import subprocess


class Git(AbstractVCS):
    @staticmethod
    def get_current_commit():
        output = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .strip()
            .decode()
        )
        if "fatal: not a git repository (or any of the parent directories)" in output:
            return "UNKNOWN"
        else:
            return output
