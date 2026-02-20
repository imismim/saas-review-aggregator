from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SubscriptionPrice, UserSubscription 
from helpers.billing import cancel_subscription
# Create your views here.



class CancelSubscriptionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('profile')

    def post(self, request, *args, **kwargs):
        user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
        
        stripe_id = user_sub_obj.stripe_id
        
        if stripe_id and user_sub_obj.is_active_status:
            try:
                sub_data = cancel_subscription(
                    stripe_id=stripe_id, 
                    reason="user requested cancellation", 
                    cancel_at_period_end=True, 
                    raw=False
                )
                
                for k, v in sub_data.items():
                    if hasattr(user_sub_obj, k):
                        setattr(user_sub_obj, k, v)
                
                user_sub_obj.save()
                
                messages.success(
                    request, 
                    "Your subscription cancellation request has been processed. "
                    "It will remain active until the end of the current billing period."
                )
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.warning(request, "No active subscription found to cancel.")

        return redirect('profile')

class SubscriptionPricingView(View):
    INT_MAP = {
        'monthly': SubscriptionPrice.IntervalChoices.MONTHLY,
        'yearly': SubscriptionPrice.IntervalChoices.YEARLY
    }
    def get(self,request, interval=None):
        qs = SubscriptionPrice.objects.filter(featured=True)        
        object_qs = qs.filter(interval=self.INT_MAP['monthly'])

        monthly_url = reverse('pricing-interval', kwargs={'interval': self.INT_MAP['monthly']})
        yearly_url = reverse('pricing-interval', kwargs={'interval': self.INT_MAP['yearly']})
        active = self.INT_MAP['monthly']
        if interval == self.INT_MAP['yearly']:
            active = self.INT_MAP['yearly']
            object_qs = qs.filter(interval=self.INT_MAP['yearly'])
        context = {
            'object_qs': object_qs,
            'monthly_url': monthly_url,
            'yearly_url': yearly_url,
            'active': active
        }
        return render(request,'subscriptions/pricing.html', context=context)
    
subscription_price_view = SubscriptionPricingView.as_view()
cancel_subscription_view = CancelSubscriptionView.as_view()
