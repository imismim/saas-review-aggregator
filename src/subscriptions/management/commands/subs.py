from django.core.management.base import BaseCommand

from subscriptions.utils import (sync_permissions,
                                 clear_dangling_subs,
                                 refresh_active_users_subscriptions)


class Command(BaseCommand):
    help = 'Sy nc subscriptions with groups and permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-perm',
            action='store_true',
            help='Sync permissions for all active subscriptions',
            default=False
        )
        parser.add_argument(
            '--dangling',
            action='store_true',
            help='Clear dangling subscriptions that exist in Stripe but not in our database',
            default=False
        )
        parser.add_argument(
            '--refresh',
            type=int,
            nargs='*',
            help='Refresh UserSubscription records for one or more users, if nothing is passed it will refresh all UserSubscription records.',
        )
        parser.add_argument(
            '--all',
            action='store_false', 
            help='Force the update even if the record is recently synced. Use with --refresh to ensure all records are updated.',
            default=True
        )

    def handle(self, *args, **kwargs):
        sync_perm = kwargs.get('sync_perm')
        dangling = kwargs.get('dangling')
        refresh = kwargs.get('refresh')

        if sync_perm:
            sync_permissions(self=self)
        elif dangling:
            clear_dangling_subs(self=self)
        elif refresh == [] or refresh:
            _all = kwargs.get('all')
            refresh_active_users_subscriptions(self=self, user_ids=refresh, only_active=_all)
        else:
            self.stdout.write(self.style.WARNING('No action specified.\nUse --sync-perm, --dangling, or --refresh.'))
