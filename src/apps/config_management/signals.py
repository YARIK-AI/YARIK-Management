from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from .RepoManager import RepoManager
from core.settings import GIT_URL

@receiver(user_logged_out)
def handle_user_logged_out(sender, user, request, **kwargs):
    if request.session.get("repo_path"):
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
        repo.del_repo_dir()


@receiver(user_logged_in)
def handle_user_logged_in(sender, user, request, **kwargs):
    repo: RepoManager = None
    if "repo_path" in request.session.keys() and request.session["repo_path"]:
        repo = RepoManager(GIT_URL, request.session.get("repo_path"))
    else: 
        repo = RepoManager(GIT_URL)
        request.session["repo_path"] = repo.temp