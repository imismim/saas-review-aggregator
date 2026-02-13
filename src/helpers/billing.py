from decouple import config
from django.conf import settings
import stripe

DEBUG = settings.DEBUG
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

if "sk_test" in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError("Stripe secret key is set to test mode but DEBUG is False")

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(name="", email="", metadata={}, raw=False):
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata,

    )    
    if raw:
        return response 
    stripe_id = response.get("id")
    return stripe_id

def create_product(name="", metadata={}, raw=False):
    response = stripe.Product.create(
        name=name,
        metadata=metadata
    )    
    if raw:
        return response 
    stripe_id = response.get("id")
    return stripe_id



def create_price(currency="usd",
    unit_amount=9999,
    interval="month",
    metadata={},
    product_stripe_id=None,
    raw=False
    ):
    response = stripe.Price.create(
                currency=currency,
                unit_amount=unit_amount,
                recurring={"interval": interval},
                product=product_stripe_id,
                metadata=metadata
            ) 
    if raw:
        return response 
    stripe_id = response.get("id")
    return stripe_id
