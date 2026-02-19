from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission 

from subscriptions.models import Subscription
from subscriptions.utils import sync_permissions
class Command(BaseCommand):
    help = 'Sy nc subscriptions with groups and permissions'

    def handle(self, *args, **kwargs):
        sync_permissions(self=self)
            