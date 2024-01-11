from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .classes import RepoManager
from core.settings import GIT_URL

@receiver(user_logged_out)
def handle_user_logged_out(sender, user, request, **kwargs):
    repo = RepoManager(GIT_URL, request.session.get("repo_path"))
    repo.del_repo_dir()