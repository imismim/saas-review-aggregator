from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription
from helpers.billing import (start_checkout_session,
                             get_checkout_session,
                             get_subscription,
                             get_checkout_customer_plan)
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
    customer_id, plan_id = get_checkout_customer_plan(session_id=session_id)
    try:
        sub_obj =  Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
    except:
        sub_obj = None
    
    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except:
        user_obj = None
        
    try:
        user_sub_obj, created = UserSubscription.objects.get_or_create(user=user_obj, 
                                                                       defaults={'subscription': sub_obj})
    except:
        user_sub_obj = None
        
    if None in [sub_obj, user_obj, user_sub_obj]:
        return HttpResponse("Something went wrong while processing your subscription. Please contact support.")
         
    context = {
 
    }
 
    return render(request, 'checkouts/success.html', context=context)