from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse

from subscriptions.models import SubscriptionPrice
from helpers.billing import (start_checkout_session,
                             get_checkout_session,
                             get_subscription)
# Create your views here.

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe-checkout-start')

@login_required
def checkout_redirect_view(request):
    subscription_price_id = request.session.get('checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=subscription_price_id)
    except:
        obj = None
    if subscription_price_id is None or obj is None:
        return redirect('pricing')

    customer_stripe_id = request.user.customer.stripe_customer_id
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


def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    checkout_response = get_checkout_session(stripe_id=session_id)
    sub_stripe_id = checkout_response.get("subscription")
    sub_response = get_subscription(stripe_id=sub_stripe_id)
    
    customer_id = checkout_response.get("customer")
    
    sub_plan = sub_response.get("plan", {})
    subs_plan_stripe_id = sub_plan.get("id")
    price_qs = SubscriptionPrice.objects.filter(stripe_id=subs_plan_stripe_id)
    print("price_qs", price_qs)
    
    context = {
        "checkout ": checkout_response,
        "subscription": sub_response
    }
 
    return render(request, 'checkouts/success.html', context=context)