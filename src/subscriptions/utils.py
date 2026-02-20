from helpers.billing import (get_customer_list_subscriptions, 
                             cancel_subscription, 
                             get_subscription)
from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription

def get_self(self=None):
    out = self.stdout.write if self else print 
    style_success = self.style.SUCCESS if self else lambda x: x
    style_error = self.style.ERROR if self else lambda x: x
    return out, style_success, style_error

def refresh_active_users_subscriptions(self=None, user_ids=None, only_active=False):
    
    out, style_success, style_error = get_self(self)
    if only_active:
        users_subs_qs = UserSubscription.objects.all_active()
    else:   
        users_subs_qs = UserSubscription.objects.all()
    
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