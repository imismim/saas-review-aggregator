from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages as message

from .models import SubscriptionPrice, UserSubscription 
from helpers.billing import cancel_subscription
# Create your views here.


def cancel_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        stripe_id = user_sub_obj.stripe_id
        if stripe_id and user_sub_obj.is_active_status:
            sub_data = cancel_subscription(
                stripe_id=stripe_id, reason="user requested cancellation", 
                cancel_at_period_end=True, raw=False)
            print("cancel subscription response", sub_data)
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)   
            user_sub_obj.save()
            message.success(request, "Your subscription cancellation request has been processed. Your subscription will remain active until the end of the current billing period.")    
             
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
