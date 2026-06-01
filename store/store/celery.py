# точка входа Celery для Django проекта.

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "store.settings")

app = Celery("store")

# namespace="CELERY" - загружай из settings.py только настройки начинающиеся с CELERY_”
app.config_from_object("django.conf:settings", namespace="CELERY")

# автоматически найди все tasks.py во всех Django apps
app.autodiscover_tasks()
