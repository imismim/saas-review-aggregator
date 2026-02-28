from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurants-list'),
    path('add/', views.restaurant_add, name='restaurant-add'),
    path('<slug:slug>/', views.restaurant_detail, name='restaurant-detail'),
    path('<slug:slug>/edit/', views.restaurant_edit, name='restaurant-edit'),
    path('<slug:slug>/delete/', views.restaurant_delete, name='restaurant-delete'),
    path('<int:pk>/active-toggle/', views.restaurant_active_toggle, name='restaurant-active-toggle'),
]
