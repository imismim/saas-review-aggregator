from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from .models import Restaurant
from .mixions import SubscriptionRequiredMixin, RestaurantLimitMixin
from helpers.google_seach import search_restaurants, get_restaurant_details
import logging

logger = logging.getLogger(__name__)

class RestaurantListView(LoginRequiredMixin,
                         ListView):
    model = Restaurant
    template_name = 'restaurants/restaurants_list.html'
    context_object_name = 'restaurants'


class RestaurantDetailView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    
    messages_text_no_sub = "You need an active subscription to view restaurant details."
    messages_text_no_user_sub = "You need to subscribe to view restaurant details."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to view restaurant details."


class RestaurantDeleteView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           DeleteView):
    model = Restaurant
    template_name = 'restaurants/restaurant_confirm_delete.html'
    success_url = reverse_lazy('restaurants-list')
    
    messages_text_no_sub = "You need an active subscription to delete a restaurant."
    messages_text_no_user_sub = "You need to subscribe to delete a restaurant."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to delete a restaurant."

class RestaurantActiveTogglefView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        active = request.POST.get('status')
        
        restaurant = get_object_or_404(Restaurant, user=request.user, pk=pk)
        restaurant.active = active == 'True'
        restaurant.save(update_fields=['active'])
        
        return redirect('restaurant-detail', slug=restaurant.slug)

class SearchRestaurant(LoginRequiredMixin,SubscriptionRequiredMixin, TemplateView):
    template_name = 'restaurants/restaurant_search.html'


class RestaurantSearchAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 3:
            return JsonResponse({'results': []})
        
        try:
            results = search_restaurants(query)
            print(f"Search results: {results}")
            return JsonResponse({'results': results})
        except Exception as e:
            logger.error(f"Google Places search error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
class RestaurantAddFromGoogleView(LoginRequiredMixin, SubscriptionRequiredMixin, RestaurantLimitMixin, View):
    def post(self, request, *args, **kwargs):
        place_id = request.POST.get('place_id')
        
        if not place_id:
            messages.error(request, "No place selected.")
            return redirect('restaurant-search')
        
        restaurant_data = get_restaurant_details(place_id)
        restaurant_obj, created = Restaurant.objects.get_or_create(user=request.user, 
                                                                   place_id=place_id, 
                                                                   defaults=restaurant_data)
        
        if not created:
            messages.info(request, f"{restaurant_obj.name} is already in your list.")
        else:
            messages.success(request, f"{restaurant_obj.name} added successfully!")
            
        return redirect('restaurant-detail', slug=restaurant_obj.slug)

        
    
restaurant_list = RestaurantListView.as_view()
restaurant_detail = RestaurantDetailView.as_view()
restaurant_delete = RestaurantDeleteView.as_view()
restaurant_active_toggle = RestaurantActiveTogglefView.as_view()
restaurant_add_from_google = RestaurantAddFromGoogleView.as_view()
search_restaurant = SearchRestaurant.as_view()
restaurant_search_api = RestaurantSearchAPIView.as_view()   