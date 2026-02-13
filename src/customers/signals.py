from allauth.account.signals import (
    user_signed_up,
    email_confirmed
)
from django.dispatch import receiver

from .models import Customer

@receiver(user_signed_up)
def user_signed_up_handler(sender, request, user, *args, **kwargs):
    from allauth.account.models import EmailAddress
    
    email = user.email
    is_verified = EmailAddress.objects.filter(
        user=user, 
        email=email, 
        verified=True
    ).exists()

    Customer.objects.create(
        user=user, 
        init_email=email,
        init_email_confirmed=is_verified
    )

@receiver(email_confirmed)
def email_confirmed_handler(sender, request, email_address, *args, **kwargs):
    qs = Customer.objects.filter(init_email=email_address)
    if qs.exists():
        customer = qs.first()
        customer.init_email_confirmed = True
        customer.save()
      
      
  