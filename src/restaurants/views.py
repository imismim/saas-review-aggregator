from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Restaurant
from .form import RestaurantForm
from .mixions import SubscriptionRequiredMixin, RestaurantLimitMixin

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


class RestaurantCreateView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           RestaurantLimitMixin,
                           CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_add.html'
    success_url = reverse_lazy('restaurants-list')
    
    messages_text_no_sub = "You need an active subscription to add a restaurant."
    messages_text_no_user_sub = "You need to subscribe to add a restaurant."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to add a restaurant."
    messages_text_max_count = "You have reached the maximum number of restaurants allowed by your subscription. Please upgrade your subscription to add more restaurants."
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_edit.html'
    
    messages_text_no_sub = "You need an active subscription to edit a restaurant."
    messages_text_no_user_sub = "You need to subscribe to edit a restaurant."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to edit a restaurant."
    
    def get_success_url(self):
        return reverse_lazy('restaurant-detail', kwargs={'slug': self.object.slug})


class RestaurantDeleteView(LoginRequiredMixin,
                           SubscriptionRequiredMixin,
                           DeleteView):
    model = Restaurant
    template_name = 'restaurants/restaurant_confirm_delete.html'
    success_url = reverse_lazy('restaurants-list')
    
    messages_text_no_sub = "You need an active subscription to delete a restaurant."
    messages_text_no_user_sub = "You need to subscribe to delete a restaurant."
    messages_text_inactive_sub = "Your subscription is not active. Please subscribe to delete a restaurant."
    


restaurant_list = RestaurantListView.as_view()
restaurant_detail = RestaurantDetailView.as_view()
restaurant_add = RestaurantCreateView.as_view()
restaurant_edit = RestaurantUpdateView.as_view()
restaurant_delete = RestaurantDeleteView.as_view()