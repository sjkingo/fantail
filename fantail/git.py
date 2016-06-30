"""
Module for interacting with Git repositories.

The `git` command must be on PATH for this to work, or you must pass
the full path to GitRepository.__init__.
"""

import logging
import subprocess

class GitRepository(object):
    repo_path = None
    git_cmd = None

    def __init__(self, repo_path, git_cmd='git'):
        self.repo_path = repo_path
        self.git_cmd = git_cmd
        self.git_init()

    def _run(self, args):
        """
        Runs the git command with the arguments specified.
        If the command fails, writes the error to the warning logger and
        returns False.
        Otherwise, returns the output or None if there was none.
        """

        git_args = [self.git_cmd, '-C', self.repo_path] + args
        logging.debug('Going to call ' + ' '.join(git_args))

        try:
            output = subprocess.check_output(git_args, stderr=subprocess.STDOUT)
            stdout = str(output, 'utf-8').strip()
        except subprocess.CalledProcessError as e:
            logging.warning(e.output)
            return False # error

        if len(stdout) > 0:
            # success with output
            logging.debug(stdout)
            return stdout
        else:
            # success with no output
            return None

    def git_init(self):
        """
        Initialises a repository.
        """
        self._run(['init', '.'])

    def git_add_all(self):
        """
        Adds changes from all tracked and untracked files to the staging area.
        """
        self._run(['add', '-A'])

    def git_commit(self, msg='fantail build'):
        """
        Commits changes to the staging area to the tree.
        """
        self._run(['commit', '-q', '-m', msg])
