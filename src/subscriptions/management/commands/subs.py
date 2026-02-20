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
        parser.add_argument(
            '--days-left',
            type=int, 
            help='Only refresh subscriptions that have less than the specified number of days left before expiration. Use with --refresh to target specific subscriptions.',
            default=0
        )
        parser.add_argument(
            '--days-ago',
            type=int, 
            help='Only refresh subscriptions that have expired more than the specified number of days ago. Use with --refresh to target specific subscriptions.',
            default=0
        )
        
        parser.add_argument(
            '--days-range',
            type=int,
            nargs=2,
            help='Only refresh subscriptions that have expired within the specified number of days range. Use with --refresh to target specific subscriptions. Example: --days-range 7 30 will refresh subscriptions that expired between 7 and 30 days left.',
            default=[0, 0]
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
            days_left = kwargs.get('days_left')
            days_ago = kwargs.get('days_ago')
            days_range = kwargs.get('days_range')
            refresh_active_users_subscriptions(self=self, 
                                               user_ids=refresh, 
                                               only_active=_all, 
                                               days_left=days_left, 
                                               days_ago=days_ago,
                                               days_range=days_range)
        else:
            self.stdout.write(self.style.WARNING('No action specified.\nUse --sync-perm, --dangling, or --refresh.'))
