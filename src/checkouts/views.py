from django.shortcuts import render,redirect,  get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
import logging
import stripe

from restaurants.models import Restaurant
from subscriptions.models import SubscriptionPrice, Subscription
from helpers.billing import (start_checkout_session,
                             get_checkout_customer_plan)
from . import webhooks

# Create your views here.

User = get_user_model()
logger = logging.getLogger(__name__)



class StartCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'checkouts/select_active_restaurant.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        price_id = self.kwargs.get('price_id')
        sub_price_obj = get_object_or_404(SubscriptionPrice, id=price_id)
        sub_obj = sub_price_obj.subscription
        
        context['max_count'] = sub_obj.max_count_restaurant
        context['restaurants'] = Restaurant.objects.filter(user=self.request.user)
        context['price_id'] = price_id
        
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        if context['max_count'] >= context['restaurants'].count():
            return self.post(request, *args, **kwargs)
        
        return render(request, self.template_name, context=context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        price_id = context['price_id']
        max_count = context['max_count']
        restaurant_ids_lst = request.POST.getlist('restaurant_ids')
            
        if max_count < len(restaurant_ids_lst):
            messages.warning(request, f"You can only select up to {max_count} restaurants. You selected {len(restaurant_ids_lst)}.")
            return redirect('sub-price-checkout', price_id=price_id)
                
        sub_price_obj = get_object_or_404(SubscriptionPrice, id=price_id)
        customer_stripe_id = request.user.customer.stripe_id
        successful_url = request.build_absolute_uri(reverse('stripe-checkout-end'))
        cancel_url = request.build_absolute_uri(reverse('pricing'))
        restaurant_ids = ','.join(restaurant_ids_lst)
        
        url = start_checkout_session(
            customer_id=customer_stripe_id,
            successful_url=successful_url,
            cancel_url=cancel_url,
            price_stripe_id=sub_price_obj.stripe_id,
            sub_metadata={"selected_restaurant_ids": restaurant_ids},
            raw=False
        )
        
        return redirect(url)
    
    
class CheckoutFinalizeView(LoginRequiredMixin, TemplateView):
    template_name = 'checkouts/success.html'
    
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        
        if not session_id:
            logger.warning(f"Session id not found in request. {request.GET}")
            return redirect('pricing')
        
        checkout_data = get_checkout_customer_plan(session_id=session_id)
        plan_id = checkout_data.pop("plan_id")
        
        try:
            sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
        except Subscription.DoesNotExist:
            logger.error(f"Subscription not found for plan_id: {plan_id}")
            return redirect('pricing')
        
        logger.info(f"Checkout complete for user: {request.user.username} plan: {sub_obj.name}")
        
        return render(request, self.template_name, {'subscription': sub_obj})



class StripeWebhookView(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
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
            'customer.subscription.updated': webhooks.handle_subscription_updated,
            'customer.subscription.created': webhooks.handle_subscription_created,
            'customer.subscription.deleted': webhooks.handle_subscription_deleted,
            'invoice.payment_failed': webhooks.handle_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Handler crashed for {event_type}: {e}", exc_info=True)
        else:
            logger.debug(f"Unhandled event: {event_type}")

        return HttpResponse(status=200)


stripe_webhook_view = StripeWebhookView.as_view()
start_checkout_view = StartCheckoutView.as_view()
checkout_finalize_view = CheckoutFinalizeView.as_view()