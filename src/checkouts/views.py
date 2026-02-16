from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse

from subscriptions.models import SubscriptionPrice
from helpers.billing import start_checkout_session
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
    return HttpResponse("Checkout finalized. Implement webhook to handle post-checkout actions.", status=200)