import os
import ssl
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reviewaggregator.settings')

app = Celery('reviewaggregator')

REDIS_URL = config('REDIS_URL', default='redis://redis:6379/0')

app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if REDIS_URL.startswith('rediss://'):
    ssl_config ={
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_check_hostname': False,
    }
    app.conf.broker_use_ssl = ssl_config
    app.conf.redis_backend_use_ssl = ssl_config

    app.conf.broker_transport_options = {
        'visibility_timeout': 3600,
        'socket_timeout': 30,
        'socket_connect_timeout': 30,
        'retry_on_timeout': True,
    }

app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = 10

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')