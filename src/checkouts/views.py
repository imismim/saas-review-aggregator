from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import logging
import stripe

from subscriptions.models import SubscriptionPrice, Subscription
from helpers.billing import (start_checkout_session,
                             get_checkout_customer_plan)
from . import webhooks

# Create your views here.

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required
def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe-checkout-start')


@login_required
def checkout_redirect_view(request):
    subscription_price_id = request.session.get(
        'checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=subscription_price_id)
    except SubscriptionPrice.DoesNotExist as e:
        logger.error(f"SubscriptionPrice not found for id: {subscription_price_id}")
        return redirect('pricing')

    customer_stripe_id = request.user.customer.stripe_id
    successful_url = request.build_absolute_uri(reverse('stripe-checkout-end'))
    cancel_url = request.build_absolute_uri(reverse('pricing'))

    url = start_checkout_session(
        customer_id=customer_stripe_id,
        successful_url=successful_url,
        cancel_url=cancel_url,
        price_stripe_id=obj.stripe_id,
        raw=False
    )
    return redirect(url)

@login_required
def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    
    if session_id is None:
        logger.warning(f"Session id not found in request. {request.GET}")
        return redirect('pricing')
    
    checkout_data = get_checkout_customer_plan(session_id=session_id)
    plan_id = checkout_data.pop("plan_id")


    try:
        sub_obj = Subscription.objects.get(
            subscriptionprice__stripe_id=plan_id)
    except Subscription.DoesNotExist:
        logger.error(f"Subscription not found for plan_id: {plan_id}")
        return redirect('pricing')
                                              
    
    logger.info(f"Checkout complete for user: {request.user.username} plan: {sub_obj.name}")

    context = {
        "subscription": sub_obj,
    }
    
    return render(request, 'checkouts/success.html', context=context)


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    logger.info("Received Stripe webhook")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not sig_header:
        logger.warning("Missing Stripe-Signature header")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    event_type = event.get('type')
    event_data = event['data']['object']
    logger.info(f"Stripe webhook: {event_type}")

    handlers = {
        'customer.subscription.created': webhooks.handle_subscription_created,
        'customer.subscription.updated': webhooks.handle_subscription_updated,
        'customer.subscription.deleted': webhooks.handle_subscription_deleted,
        'invoice.payment_failed': webhooks.handle_payment_failed,
        'invoice.payment_succeeded': webhooks.handle_payment_succeeded,
        'customer.subscription.trial_ending': webhooks.handle_trial_ending,
    }

    handler = handlers.get(event_type)
    if handler:
        handler(event_data)
    else:
        logger.debug(f"Unhandled event: {event_type}")

    return HttpResponse(status=200)