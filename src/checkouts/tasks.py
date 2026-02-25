from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from reviewaggregator.constants import (PLAN_EMAIL_SUBJECT, 
                                        PLAN_EMAIL_MESSAGE, 
                                        CANCEL_EMAIL_SUBJECT, 
                                        CANCEL_EMAIL_MESSAGE)

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_greating_updated_plan(self, username, user_email, plan_name):

    try:
        send_mail(
            subject=PLAN_EMAIL_SUBJECT,
            message=PLAN_EMAIL_MESSAGE(username, plan_name),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_cancellation_email(self, username, user_email):

    try:
        send_mail(
            subject=CANCEL_EMAIL_SUBJECT,
            message=CANCEL_EMAIL_MESSAGE(username),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)