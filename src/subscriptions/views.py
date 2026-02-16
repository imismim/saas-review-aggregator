from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .models import SubscriptionPrice 
# Create your views here.


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
