from django.apps import AppConfig


class TransportConfig(AppConfig):
    name = 'transport'

    def ready(self):
        from .scheduler.scheduler import start
        start()
