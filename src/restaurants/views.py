from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from .models import Restaurant

class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/restaurants_list.html'
    context_object_name = 'restaurants'
    
    
class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    
restaurant_list = RestaurantListView.as_view()
restaurant_detail = RestaurantDetailView.as_view()