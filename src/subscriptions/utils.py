from helpers.billing import get_customer_list_subscriptions, cancel_subscription
from customers.models import Customer
from subscriptions.models import UserSubscription, Subscription


def clear_dangling_subs(self=None):
    out = self.stdout.write if self else print
    style_success = self.style.SUCCESS if self else lambda x: x
    
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
    out = self.stdout.write if self else print
    style_success = self.style.SUCCESS if self else lambda x: x
    qs = Subscription.objects.filter(active=True)
    for sub in qs:
        perms = sub.permissions.all()
        for group in sub.groups.all():
            group.permissions.set(perms) 
        
    out(style_success('Successfully synced subscriptions'))