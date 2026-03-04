from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurants-list'),
    path('search/', views.search_restaurant, name='restaurant-search'),
    path('search/api/', views.restaurant_search_api, name='restaurant-search-api'),
    path('add-from-google/', views.restaurant_add_from_google, name='restaurant-add-google'),
    path('<slug:slug>/', views.restaurant_detail, name='restaurant-detail'),
    path('<slug:slug>/delete/', views.restaurant_delete, name='restaurant-delete'),
    path('<int:pk>/active-toggle/', views.restaurant_active_toggle, name='restaurant-active-toggle'),
    
]
