from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from .RepoManager import RepoManager
from core.settings import GIT_URL, AIRFLOW_HOST, AIRFLOW_PORT
from .globals import SPN

import logging, requests

logger = logging.getLogger(__name__)

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

AIRFLOW_URL = f"http://{AIRFLOW_HOST}:{AIRFLOW_PORT}"

AUTH = ('admin', 'admin')

@receiver(user_logged_out)
def handle_user_logged_out(sender, user, request, **kwargs):
    logger.info(f'User {user} logged out.')
    if request.session.get("repo_path"):
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
        repo.del_repo_dir()


@receiver(user_logged_in)
def handle_user_logged_in(sender, user, request, **kwargs):
    logger.info(f'User {user} logged in.')
    repo: RepoManager = None

    try:
        requests.get(f"{AIRFLOW_URL}/api/v1/dags", headers=HEADERS, auth=AUTH, timeout=1)
        request.session[SPN.AIRFLOW_CONN_GOOD] = True
    except requests.exceptions.ConnectionError as e:
        request.session[SPN.AIRFLOW_CONN_GOOD] = False
    except Exception as e:
        request.session[SPN.AIRFLOW_CONN_GOOD] = False

    if "repo_path" in request.session.keys() and request.session["repo_path"]:
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
    else: 
        repo = RepoManager(GIT_URL)
        request.session["repo_path"] = repo.temp