import git
import tempfile
import shutil
import os
import datetime

import logging

logger = logging.getLogger(__name__)

class RepoManager:

    def get_file_as_str(self, gitslug:str):
        return open(os.path.join(self.temp, gitslug)).read()


    def override_file(self, gitslug:str, content:str):
        with open(os.path.join(self.temp, gitslug), "w") as f:
            f.write(content)

        self.repo.index.add([gitslug])


    def commit_changes(self):
        if self.repo.is_dirty(untracked_files=True):
            logger.info(f'{datetime.datetime.now()}:Changes detected.')
            self.repo.index.commit(
                "Change with configuration interface in "
                + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            )
            self.repo.remotes.origin.push()
            return True
        else:
            return False


    def __init__(self, git_url:str, git_path:str=None):
        if git_path:
            self.temp = git_path
            logger.info(f'{datetime.datetime.now()}: Using existing temp folder "{self.temp}"!')
            self.repo = git.Repo(self.temp)
            logger.info(f'{datetime.datetime.now()}: Using existing repo in "{self.temp}"!')
        else:
            self.temp = tempfile.mkdtemp(prefix="temp_repo_dir_")
            logger.info(f'{datetime.datetime.now()}: Temp folder "{self.temp}" created!')
            self.repo = git.Repo.clone_from(git_url, self.temp)
            logger.info(f'{datetime.datetime.now()}: Repo "{git_url}" cloned to temp folder "{self.temp}"!')


    def del_repo_dir(self):
        path = self.temp
        shutil.rmtree(self.temp)
        logger.info(f"{datetime.datetime.now()}: Temp folder {path} deleted!")

