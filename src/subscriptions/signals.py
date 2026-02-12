from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserSubscription, Subscription

ALLOW_CUSTOM_GROUPS = True

@receiver(post_save, sender=UserSubscription)
def update_user_permissions(sender, instance, created, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription = user_sub_instance.subscription
    groups_ids = []
    if subscription is not None:
        groups = subscription.groups.all()
        groups_ids = groups.values_list('id', flat=True)

    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if subscription is not None:
            subs_qs = subs_qs.exclude(id=subscription.id)
            
        subs_groups_ids = subs_qs.values_list('groups__id', flat=True)
        subs_groups_ids_set = set(subs_groups_ids)
        
        groups_ids_set = set(groups_ids)

        currunt_groups = user.groups.all().values_list('id', flat=True)
        currunt_groups_set = set(currunt_groups) - subs_groups_ids_set

        final_group_ids  = list(groups_ids_set | currunt_groups_set)
        user.groups.set(final_group_ids)
    print(f"Updated permissions for user {user.username} to {subscription.name}")