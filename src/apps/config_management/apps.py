from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_out

class ConfigManagementConfig(AppConfig):
    name = "apps.config_management"
    label = "Configuration"

    from . import signals

    user_logged_out.connect(signals.handle_user_logged_out)
