from django.db import models
from django.conf import settings
from helpers.billing import create_customer
# Create your models here.

User = settings.AUTH_USER_MODEL


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(
        max_length=100, null=True, blank=True)
    init_email = models.EmailField(null=True, blank=True)
    init_email_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.stripe_customer_id:
            if self.init_email and self.init_email_confirmed: 
                email = self.init_email
                stripe_customer_id = create_customer(email=email, metadata={
                    "user_id": self.user.id, "username": self.user.username
                    })
                self.stripe_customer_id = stripe_customer_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}"
