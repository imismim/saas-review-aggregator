from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Restaurant
from .form import RestaurantForm


class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/restaurants_list.html'
    context_object_name = 'restaurants'


class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_add.html'
    success_url = reverse_lazy('restaurants-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class RestaurantUpdateView(LoginRequiredMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_edit.html'

    def get_success_url(self):
        return reverse_lazy('restaurant-detail', kwargs={'slug': self.object.slug})


class RestaurantDeleteView(LoginRequiredMixin, DeleteView):
    model = Restaurant
    template_name = 'restaurants/restaurant_confirm_delete.html'
    success_url = reverse_lazy('restaurants-list')


restaurant_list = RestaurantListView.as_view()
restaurant_detail = RestaurantDetailView.as_view()
restaurant_add = RestaurantCreateView.as_view()
restaurant_edit = RestaurantUpdateView.as_view()
restaurant_delete = RestaurantDeleteView.as_view()