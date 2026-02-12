from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission 
from subscriptions.models import Subscription

class Command(BaseCommand):
    help = 'Sy nc subscriptions with groups and permissions'

    def handle(self, *args, **kwargs):
        qs = Subscription.objects.filter(active=True)
        for sub in qs:
            perms = sub.permissions.all()
            for group in sub.groups.all():
                group.permissions.set(perms) 
        
        self.stdout.write(self.style.SUCCESS('Successfully synced subscriptions'))
                
            