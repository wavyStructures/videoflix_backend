from django.apps import AppConfig


class VideoflixAppConfig(AppConfig):
    """
    App configuration for the videoflix_app.
    Loads signal handlers when the app is ready so they register
    automatically on startup.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix_app'
    
    def ready(self):
        import videoflix_app.signals

