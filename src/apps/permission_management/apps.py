from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_out
from apps.config_management import signals

class ConfigManagementConfig(AppConfig):
    name = "apps.permission_management"
    label = "Permissions"

    user_logged_out.connect(signals.handle_user_logged_out)
