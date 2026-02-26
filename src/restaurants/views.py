from django.shortcuts import render
from django.views.generic import ListView, TemplateView

# Create your views here.


class RestaurantListView(TemplateView):
    template_name = 'restaurants/restaurants_list.html'
    context_object_name = 'restaurants'
    
    

restaurant_list = RestaurantListView.as_view()