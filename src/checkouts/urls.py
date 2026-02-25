from django.urls import path

from checkouts import views as checkout_views

urlpatterns = [
    path('sub_prices/<int:price_id>/', checkout_views.product_price_redirect_view, name='sub-price-checkout'),
    path('start/', checkout_views.checkout_redirect_view, name='stripe-checkout-start'),
    path('success/', checkout_views.checkout_finalize_view, name='stripe-checkout-end'),
    path('webhooks/', checkout_views.stripe_webhook_view, name='stripe-webhook'),
]
