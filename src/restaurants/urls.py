from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurants-list'),
    path('<slug:slug>/', views.restaurant_detail, name='restaurant-detail'),
]
