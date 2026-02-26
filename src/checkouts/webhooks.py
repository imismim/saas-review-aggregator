import stripe
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
import json

from subscriptions.models import UserSubscription, Subscription, SubscriptionStatus
from helpers.billing import serialize_subscription_data_from_webhook, cancel_subscription
from .tasks import send_greating_updated_plan, send_cancellation_email, send_payment_failed_email
from restaurants.models import Restaurant
logger = logging.getLogger(__name__)
User = get_user_model()


def handle_subscription_created(sub_data):
    stripe_id = sub_data.get('id')
    customer_id = sub_data.get('customer')
        
    if not stripe_id:
        logger.warning("subscription.created: no stripe_id in event data")
        return
    
    try:
        user = User.objects.get(customer__stripe_id=customer_id)
        
        user_sub_data = serialize_subscription_data_from_webhook(sub_data)   
          
        product_id = user_sub_data.pop('product_id')
        sub = Subscription.objects.get(stripe_id=product_id)
        
        user_sub_obj, created = UserSubscription.objects.get_or_create(user=user)
        user_sub_obj.previous_stripe_id = user_sub_obj.stripe_id
        
        for k, v in user_sub_data.items():
            if hasattr(user_sub_obj, k):
                setattr(user_sub_obj, k, v) 
                
        user_sub_obj.subscription = sub
        user_sub_obj.save()
        
        logger.info(f"subscription.created: {stripe_id} user={user.username} created={created}")
    except User.DoesNotExist:
        logger.warning(f"subscription.created: user not found for customer: {customer_id}")
        return
    except Subscription.DoesNotExist:
        logger.warning(f"subscription.created: subscription not found for product_id: {product_id}")
        return
    
    
    
def handle_subscription_updated(sub_data):
    stripe_id = sub_data.get('id')
    customer_id = sub_data.get('customer')
        
    if not stripe_id:
        logger.warning("subscription.updated: no stripe_id in event data")
        return
    
    try:
        user = User.objects.get(customer__stripe_id=customer_id)
        
        user_sub_data = serialize_subscription_data_from_webhook(sub_data)
        user_sub_obj = UserSubscription.objects.get(user=user)
        product_id = user_sub_data.pop('product_id')
        
        sub = Subscription.objects.get(stripe_id=product_id)
        
        for k, v in user_sub_data.items():
            if hasattr(user_sub_obj, k):
                setattr(user_sub_obj, k, v)
        user_sub_obj.subscription = sub
        user_sub_obj.save()
        
        cancel_at_period_end = user_sub_obj.cancel_at_period_end
        previous_stripe_id = user_sub_obj.previous_stripe_id
        status = user_sub_obj.status
        
        username = user.username
        user_email = user.email
        plan_name = sub.name
        
        if previous_stripe_id and status == SubscriptionStatus.ACTIVE:
            cancel_subscription(previous_stripe_id, reason=f"user updated subscription to {plan_name}")
        
        
        if not cancel_at_period_end:
            send_greating_updated_plan.delay(username, user_email, plan_name)
        else:
            send_cancellation_email.delay(username, user_email) 
        
        logger.info(f"subscription.updated: stripe_id={stripe_id} status={user_sub_obj.status}")
    except User.DoesNotExist:
        logger.warning(f"subscription.updated: user not found for customer: {customer_id}")
        return
    except UserSubscription.DoesNotExist:
        logger.warning(f"subscription.updated: user subscription not found for user: {user.username}")
        return

    

def handle_subscription_deleted(sub_data):
    stripe_id = sub_data.get('id')
    cancellation_details = sub_data.get('cancellation_details', {})
    cancellation_comment = cancellation_details.get('comment')
    
    if not stripe_id:
        logger.warning("subscription.deleted: no stripe_id in event data")
        return
    
    try:
        if not cancellation_comment and 'user updated subscription' not in cancellation_comment:
            user_sub_data = serialize_subscription_data_from_webhook(sub_data)
            user_sub = UserSubscription.objects.get(stripe_id=stripe_id)
            
            for k, v in user_sub_data.items():
                if hasattr(user_sub, k):
                    setattr(user_sub, k, v)
            user_sub.save()
            
            logger.info(f"subscription.deleted: {stripe_id}")
            
            username = user_sub.user.username
            user_email = user_sub.user.email
            
            send_cancellation_email.delay(
                username=username,
                user_email=user_email
            )
            Restaurant.objects.filter(user=user_sub.user, active=True).update(active=False)
            
            
    except UserSubscription.DoesNotExist:
        logger.warning(f"subscription.deleted: not found {stripe_id}")
        return

def handle_payment_failed(invoice_data):
    customer_id = invoice_data.get('customer')
    if not customer_id:
        logger.warning("payment.failed: missing customer_id or subscription_id in event data")
        return
    
    try:
        user = User.objects.get(customer__stripe_id=customer_id)
        
        username = user.username
        user_email = user.email
        
        logger.info(f"Payment failed for user: {username}")
        
        send_payment_failed_email.delay(
            username=username,
            user_email=user_email
        )
        
    except User.DoesNotExist:
        logger.warning(f"payment.failed: user not found: {customer_id}")

def handle_payment_succeeded(invoice_data):
    ...

def handle_trial_ending(sub_data):
    ...
