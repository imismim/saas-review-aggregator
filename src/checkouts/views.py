from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from helpers.billing import (start_checkout_session,
                             get_checkout_customer_plan,
                             cancel_subscription)
# Create your views here.

User = get_user_model()

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


def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    customer_id, plan_id, sub_stripe_id = get_checkout_customer_plan(session_id=session_id)
    
    try:
        sub_obj =  Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except:
        return HttpResponse("Required data not found.")
        
    user_sub_qs = UserSubscription.objects.filter(user=user_obj)
    old_stripe_id = None
    if user_sub_qs.exists():
        old_stripe_id = user_sub_qs.first().stripe_id
        
    user_sub_obj, created = UserSubscription.objects.update_or_create(user=user_obj, 
                                                                       defaults={'subscription': sub_obj,
                                                                                 'stripe_id': sub_stripe_id,
                                                                                 'user_cancelled': False})
    
    if old_stripe_id and old_stripe_id != sub_stripe_id:
        try:
            cancel_subscription(stripe_id=old_stripe_id, reason="update_subscription", raw=False)
        except:
            return HttpResponse("Could not cancel old subscription. Please contact support.")

    context = {
        "subscription": sub_obj,
    }
 
    return render(request, 'checkouts/success.html', context=context)