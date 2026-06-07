from django.apps import AppConfig


class AdminManagerConfig(AppConfig):
    name = 'admin_manager'
    def ready(self):
        import admin_manager.signals
