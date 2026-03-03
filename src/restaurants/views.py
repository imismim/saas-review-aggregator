from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Restaurant
from .mixions import SubscriptionRequiredMixin, RestaurantLimitMixin, RestaurantLimitActiveMixin
from helpers.google_seach import search_restaurants, get_restaurant_details
from reviews.tasks import scrape_reviews
from reviews.models import Review

import logging

logger = logging.getLogger(__name__)

class RestaurantListView(LoginRequiredMixin,
                         ListView):
    model = Restaurant
    template_name = 'restaurants/restaurants_list.html'
    context_object_name = 'restaurants'
    paginate_by = 6

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)


class RestaurantDetailView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    
    messages_text_no_sub = "You need an active subscription to view restaurant details."
    messages_text_no_user_sub = "You need to subscribe to view restaurant details."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to view restaurant details."

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.object.active:
            reviews_qs = Review.objects.filter(
                restaurant=self.object
            )
            
            paginator = Paginator(reviews_qs, 20)
            page_number = self.request.GET.get('page')
            context['reviews_page'] = paginator.get_page(page_number)
        
        context['reviews_count'] = self.object.reviews.count()
        return context

class RestaurantDeleteView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           DeleteView):
    model = Restaurant
    template_name = 'restaurants/restaurant_confirm_delete.html'
    success_url = reverse_lazy('restaurants-list')
    
    messages_text_no_sub = "You need an active subscription to delete a restaurant."
    messages_text_no_user_sub = "You need to subscribe to delete a restaurant."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to delete a restaurant."

    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)
    
class RestaurantActiveTogglefView(LoginRequiredMixin, RestaurantLimitMixin, RestaurantLimitActiveMixin, View):
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
    
class RestaurantAddFromGoogleView(LoginRequiredMixin, SubscriptionRequiredMixin, RestaurantLimitMixin, RestaurantLimitActiveMixin, View):
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
            if self._sub.name == 'Free':  
                scrape_reviews.delay(restaurant_obj.id)
            else:
                limit_reviews = self._sub.max_count_review
                scrape_reviews.delay(restaurant_id=restaurant_obj.id, source_slug='google_full', limit=limit_reviews)
            
        return redirect('restaurant-detail', slug=restaurant_obj.slug)

        
    
restaurant_list = RestaurantListView.as_view()
restaurant_detail = RestaurantDetailView.as_view()
restaurant_delete = RestaurantDeleteView.as_view()
restaurant_active_toggle = RestaurantActiveTogglefView.as_view()
restaurant_add_from_google = RestaurantAddFromGoogleView.as_view()
search_restaurant = SearchRestaurant.as_view()
restaurant_search_api = RestaurantSearchAPIView.as_view()   