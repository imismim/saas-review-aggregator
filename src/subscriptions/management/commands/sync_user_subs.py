from django.core.management.base import BaseCommand

from subscriptions.utils import clear_dangling_subs

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        clear_dangling_subs(self=self)
                  
            