from django.urls import path

from .views import subscription_price_view, cancel_subscription_view

urlpatterns = [
     path("pricing/", subscription_price_view, name="pricing"),
     path("cancel_subscription/", cancel_subscription_view, name="cancel-subscription"),
     path("pricing/<str:interval>/", subscription_price_view, name="pricing-interval"),
]
