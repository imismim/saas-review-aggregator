import os
import ssl
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reviewaggregator.settings')

app = Celery('reviewaggregator')
REDIS_URL = config('REDIS_URL', default='redis://redis:6379/0')

app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

if REDIS_URL.startswith('rediss://'):
    app.conf.broker_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE}
    app.conf.redis_backend_use_ssl = {'ssl_cert_reqs': ssl.CERT_NONE}
    

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')