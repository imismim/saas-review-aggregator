from django.urls import path

from checkouts import views as checkout_views

urlpatterns = [
    path('start-checkout/<int:price_id>/', checkout_views.start_checkout_view, name='sub-price-checkout'),
    path('success/', checkout_views.checkout_finalize_view, name='stripe-checkout-end'),
    path('webhooks/', checkout_views.stripe_webhook_view, name='stripe-webhook'),

]
