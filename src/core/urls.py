from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('accounts/', include('allauth.urls')),
    
    # Application URLs
    path('users/', include('users.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('checkouts/', include('checkouts.urls'), name='stripe-checkout-start'),
    path('restaurants/', include('restaurants.urls')),
]
