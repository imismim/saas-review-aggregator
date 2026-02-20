from decouple import config
from django.conf import settings
import stripe
from .date_urils import timestamp_to_datetime

DEBUG = settings.DEBUG
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY

if "sk_test" in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError("Stripe secret key is set to test mode but DEBUG is False")

stripe.api_key = STRIPE_SECRET_KEY

def serialize_subscription_data(sub_response):
    status = sub_response.get("status")
    
    current_period_start = timestamp_to_datetime(sub_response.get("current_period_start"))
    current_period_end = timestamp_to_datetime(sub_response.get("current_period_end"))
    cancel_at_period_end = sub_response.get("cancel_at_period_end", False)
    
    return {
        'current_period_start': current_period_start,
        'current_period_end': current_period_end,
        'status': status,
        'cancel_at_period_end': cancel_at_period_end
    }

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

def start_checkout_session(customer_id="", successful_url="", cancel_url="", price_stripe_id="", raw=True):
    if not successful_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        successful_url += "?session_id={CHECKOUT_SESSION_ID}"
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=successful_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
        )
    if raw: 
        return response
    return response.get("url")

def get_checkout_session(stripe_id="", raw=True):
    response = stripe.checkout.Session.retrieve(stripe_id)
    if raw:
        return response
    return response.get("url")

def get_subscription(stripe_id="", raw=True):
    response = stripe.Subscription.retrieve(stripe_id)
    if raw:
        return response
    return serialize_subscription_data(response)

def get_customer_list_subscriptions(customer_stripe_id="", limit=10):
    response = stripe.Subscription.list(
        limit=limit,
        customer=customer_stripe_id,
        status="active")
    
    return response

    
def get_checkout_customer_plan(session_id=""):
    checkout_response = get_checkout_session(stripe_id=session_id)
    customer_id = checkout_response.get("customer")
    
    sub_stripe_id = checkout_response.get("subscription")
    sub_response = get_subscription(stripe_id=sub_stripe_id)
    sub_plan = sub_response.get("plan", {})
    plan_id = sub_plan.get("id")
    
    subscription_data = serialize_subscription_data(sub_response)
 
    data ={
        "customer_id": customer_id,
        "plan_id": plan_id,
        "sub_stripe_id": sub_stripe_id,
        **subscription_data
    }
    return data
 
 
def cancel_subscription(stripe_id="", reason="",
                        cancel_at_period_end=False,
                        feedback="", raw=True):

    if cancel_at_period_end:
        response = stripe.Subscription.modify(stripe_id, cancel_at_period_end=cancel_at_period_end, cancellation_details={
            "comment": reason, "feedback": feedback, })
    else:
        response = stripe.Subscription.cancel(stripe_id, cancellation_details={
            "comment": reason, "feedback": feedback})
    if raw:
        return response
    return serialize_subscription_data(response)    
