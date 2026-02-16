from django.urls import path

from .views import subscription_price_view

urlpatterns = [
     path("pricing/", subscription_price_view, name="pricing"),
     path("pricing/<str:interval>/", subscription_price_view, name="pricing-interval"),
]
