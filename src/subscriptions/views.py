from django.shortcuts import render
from django.views import View

from .models import SubscriptionPrice 
# Create your views here.


class SubscriptionPricingView(View):

    def get(self,request,  *args, **kwargs):
        qs = SubscriptionPrice.objects.filter(featured=True)
        mounthly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
        yearly_qs = qs.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
        context = {
            'mounthly_qs': mounthly_qs,
            'yearly_qs': yearly_qs
            
        }
        return render(request,'subscriptions/pricing.html', context=context)
    
subscription_price_view = SubscriptionPricingView.as_view()  
