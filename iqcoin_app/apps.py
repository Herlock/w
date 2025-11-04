from django.apps import AppConfig


class IqcoinAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iqcoin_app'
    
    def ready(self):
        import iqcoin_app.signals