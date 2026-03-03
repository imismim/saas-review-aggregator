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
            self._sub = user_sub.subscription
            if not self._sub:
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

class RestaurantLimitActiveMixin:
    messages_text_max_active_count = "You have reached the maximum number of active restaurants allowed by your subscription. Please upgrade your subscription to activate more restaurants or deactivate some of your current active restaurants."

    def dispatch(self, request, *args, **kwargs):
        status = request.POST.get('status')
        user = request.user
        user_sub = user.usersubscription
        sub = user_sub.subscription
        
        self._restaurant_active_count = Restaurant.objects.filter(user=user, active=True).count()
        self._max_allowed_active = sub.max_count_active_restaurant if sub else 0
        
        if self._max_allowed_active <= self._restaurant_active_count and status == 'True':
            messages.info(request, self.messages_text_max_active_count)
            return redirect('restaurants-list')
        
        return super().dispatch(request, *args, **kwargs)