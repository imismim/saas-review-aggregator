from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_id, subject=None, message=None):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    
    username = user.username
    try:
        send_mail(
            subject=subject,
            message=message(username),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
