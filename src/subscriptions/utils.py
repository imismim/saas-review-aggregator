from helpers.billing import (get_customer_list_subscriptions, 
                             cancel_subscription, 
                             get_subscription)
from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription, SubscriptionPrice, SUBSCRIPTION_LEVELS
from django.contrib.auth.models import Group, Permission
from django.db import transaction

def get_self(self=None):
    out = self.stdout.write if self else print 
    style_success = self.style.SUCCESS if self else lambda x: x
    style_error = self.style.ERROR if self else lambda x: x
    return out, style_success, style_error

def refresh_active_users_subscriptions(self=None, 
                                       user_ids=None, 
                                       only_active=False, 
                                       days_left=0, 
                                       days_ago=0,
                                       days_range=[0, 0]
                                    ):
    
    out, style_success, style_error = get_self(self)
    if only_active:
        users_subs_qs = UserSubscription.objects.all_active()
    else:   
        users_subs_qs = UserSubscription.objects.all()
    
    if days_left > 0:
        users_subs_qs = users_subs_qs.by_days_left(days_left=days_left)
    if days_ago > 0:
        users_subs_qs = users_subs_qs.by_days_ago(days_ago=days_ago)
        
    if days_range[0] > 0 and days_range[1] > 0:
        users_subs_qs = users_subs_qs.by_days_range(day_min=days_range[0], day_max=days_range[1])
    
    users_subs_qs = users_subs_qs.by_user_ids(user_ids=user_ids)
    
    if not users_subs_qs.exists():  
        out(style_error("No existing subscriptions for this user ids."))   
        return False
    
    success_count = 0
    qs_count = users_subs_qs.count()
    for subs in users_subs_qs:
        stripe_id = subs.stripe_id
        if stripe_id:
            refresh_user_sub_data = get_subscription(stripe_id, raw=False)
            user_sub_obj, created = UserSubscription.objects.get_or_create(stripe_id=stripe_id)
            for k, v in refresh_user_sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            out(style_success(f"Refreshed subscription for user {subs.user} - {stripe_id}"))
            success_count += 1
    
    return success_count == qs_count
    
def clear_dangling_subs(self=None):
    out, style_success, _ = get_self(self) 
    
    qs = Customer.objects.filter(stripe_id__isnull=False)
    for customer_obj in qs:
        user = customer_obj.user
        customer_stripe_id = customer_obj.stripe_id
    
        out(f"Sync {user} - {customer_stripe_id} subs and remove old")
        
        if customer_stripe_id:
            subs_response = get_customer_list_subscriptions(customer_stripe_id=customer_stripe_id, limit=50)
            for sub in subs_response:
                sub_id = sub.get('id')
                existing_user_subs_qs = UserSubscription.objects.filter(stripe_id__iexact=sub_id.strip())
                if existing_user_subs_qs.exists():
                    continue
                cancel_subscription(stripe_id=sub_id, reason="Dangling old subscription", cancel_at_period_end=False)
                out(style_success(f"--Deactivating old sub {sub_id}"))
        
    out(style_success("Syncing complete."))
                  
            
            
def sync_permissions(self=None):
    out, style_success, _ = get_self(self)
    
    qs = Subscription.objects.filter(active=True)
    for sub in qs:
        perms = sub.permissions.all()
        for group in sub.groups.all():
            group.permissions.set(perms) 
        
    out(style_success('Successfully synced subscriptions'))
    

def get_or_create_free_subscription():
    name = SUBSCRIPTION_LEVELS[0][0].capitalize()
    permssion_name = SUBSCRIPTION_LEVELS[0][1]
    
    with transaction.atomic():
        free_sub, created = Subscription.objects.get_or_create(name=name)
        
        if created:
            group, _ = Group.objects.get_or_create(name=name.capitalize())
            permissions = Permission.objects.filter(codename__in=[permssion_name])
            
            free_sub.stripe_price_id = None
            free_sub.max_count_restaurant = 1
            free_sub.max_count_review = 5
            free_sub.request_to_celery = 0
            free_sub.save()
            
            free_sub.groups.set([group])
            group.permissions.set(permissions)
            
            SubscriptionPrice.objects.create(
                subscription=free_sub,
                price=0,
                order=1,
            )
            SubscriptionPrice.objects.create(
                subscription=free_sub,
                interval=SubscriptionPrice.IntervalChoices.YEARLY,
                price=0,
                order=1,
            )
    
    return free_sub 

def set_free_subscription_for_user(user):
    free_sub = get_or_create_free_subscription()
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=user)
    if created:
        user_sub_obj.subscription = free_sub
        user_sub_obj.save()
        return True
    return False