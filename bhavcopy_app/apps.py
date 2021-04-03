from django.apps import AppConfig
import os

class BhavcopyAppConfig(AppConfig):
    name = 'bhavcopy_app'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            from . import scheduler
            scheduler.start()