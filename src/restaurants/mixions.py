from django.contrib import messages
from django.shortcuts import redirect

from .models import Restaurant
from subscriptions.models import UserSubscription  

class SubscriptionRequiredMixin:
    
    messages_text_no_sub = "You need an active subscription to access this page."
    messages_text_no_user_sub = "You need to subscribe to access this page."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to access this page."
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        try:            
            user_sub = user.usersubscription
            sub = user_sub.subscription
            if not sub:
                messages.info(request, self.messages_text_no_user_sub)
                return redirect('pricing')
        except UserSubscription.DoesNotExist:
            messages.info(request, self.messages_text_no_sub)
            return redirect('pricing')
        
        if not user_sub.is_active_status:
            messages.info(request, self.messages_text_inactive_sub)
            return redirect('pricing')
        
        return super().dispatch(request, *args, **kwargs)
    

class RestaurantLimitMixin:
    
    messages_text_max_count = "You have reached the maximum number of restaurants allowed by your subscription. Please upgrade your subscription to add more restaurants."
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        user_sub = user.usersubscription
        sub = user_sub.subscription
        
        self._restaurants_count = Restaurant.objects.filter(user=user).count()
        self._max_allowed = sub.max_count_restaurant if sub else 0
        
        if self._max_allowed <= self._restaurants_count:
            messages.info(request, self.messages_text_max_count)
            return redirect('restaurants-list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['is_max_count_restaurants'] = self._max_allowed <= self._restaurants_count
        return context