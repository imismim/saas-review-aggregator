from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings
# Create your models here.

User = settings.AUTH_USER_MODEL
SUBSCRIPTION_LEVELS = [
    ('basic', 'Basic permissions'),
    ('advanced', 'Advanced permissions'),
    ('pro', 'Pro permissions'),
]

class Subscription(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, limit_choices_to={'content_type__app_label': 'subscriptions', 
                                                                    'codename__in': [level[0] for level in SUBSCRIPTION_LEVELS]})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        permissions = SUBSCRIPTION_LEVELS

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    