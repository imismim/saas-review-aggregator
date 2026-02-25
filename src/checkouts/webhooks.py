import stripe
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
import json

from subscriptions.models import UserSubscription, Subscription
from helpers.billing import serialize_subscription_data_from_webhook

logger = logging.getLogger(__name__)
User = get_user_model()


def handle_subscription_created(sub_data):
    stripe_id = sub_data.get('id')
    customer_id = sub_data.get('customer')

    try:
        user = User.objects.get(customer__stripe_id=customer_id)
    except User.DoesNotExist:
        logger.warning(f"subscription.created: user not found for customer: {customer_id}")
        return
    
    user_sub_data = serialize_subscription_data_from_webhook(sub_data)
    product_id = user_sub_data.get('product_id')
    
    try:
        sub = Subscription.objects.get(stripe_id=product_id)
    except Subscription.DoesNotExist:
        logger.warning(f"subscription.created: subscription not found for product_id: {product_id}")
        return
    
    _, created = UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            "subscription": sub
            **user_sub_data,
        }
    )
    
    logger.info(f"subscription.created: {stripe_id} user={user.username} created={created}")
    
def handle_subscription_updated(sub_data):
    stripe_id = sub_data.get('id')
    customer_id = sub_data.get('customer')
        
    if not stripe_id:
        logger.warning("subscription.updated: no stripe_id in event data")
        return
    
    try:
        user = User.objects.get(customer__stripe_id=customer_id)
    except User.DoesNotExist:
        logger.warning(f"subscription.updated: user not found for customer: {customer_id}")
        return
        
    user_sub_data = serialize_subscription_data_from_webhook(sub_data)
    product_id = user_sub_data.get('product_id')
    
    try:
        sub = Subscription.objects.get(stripe_id=product_id)
    except Subscription.DoesNotExist:
        logger.warning(f"subscription.updated: subscription not found for product_id: {product_id}")
        return
    
    user_sub_obj, _ = UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            "subscription": sub,    
            **user_sub_data
        }
    )
    
    logger.info(f"subscription.updated: stripe_id={stripe_id} status={user_sub_obj.status}")

    

def handle_subscription_deleted(sub_data):
    ...

def handle_payment_failed(invoice_data):
    ...

def handle_payment_succeeded(invoice_data):
    ...

def handle_trial_ending(sub_data):
    ...
