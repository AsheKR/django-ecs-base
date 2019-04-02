from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "users"
    verbose_name = "Users"

    def ready(self):
        try:
            import users.signals  # pylint: disable=W0611
        except ImportError:
            pass
