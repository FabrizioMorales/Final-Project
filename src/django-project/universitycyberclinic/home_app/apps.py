from django.apps import AppConfig


class HomeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home_app'

    def ready(self):
        import home_app.signals  # Automatically register the user profile creation signal
