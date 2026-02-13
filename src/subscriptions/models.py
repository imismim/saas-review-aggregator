from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from helpers.billing import create_product, create_price
# Create your models here.

User = settings.AUTH_USER_MODEL
SUBSCRIPTION_LEVELS = [
    ('basic', 'Basic permissions'),
    ('advanced', 'Advanced permissions'),
    ('pro', 'Pro permissions'),
]

class Subscription(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, limit_choices_to={'content_type__app_label': 'subscriptions', 
                                                                    'codename__in': [level[0] for level in SUBSCRIPTION_LEVELS]})

    stripe_id = models.CharField(max_length=100, null=True, blank=True)
    
    order = models.IntegerField(default=-1)
    featured = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)    
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        permissions = SUBSCRIPTION_LEVELS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = create_product(
                name=self.name, 
                metadata={
                    "subscription_plan_id": self.id
                }
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)

class SubscriptionPrice(models.Model):
    """
    Stripe price object
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY = "month", "Monthly"
        YEARLY = "year", "Yearly"
    
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_id = models.CharField(max_length=100, null=True, blank=True)
    interval = models.CharField(max_length=10, 
                                choices=IntervalChoices.choices, 
                                default=IntervalChoices.MONTHLY
                            )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1)
    featured = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:  
        ordering = ('subscription__order', 'order','featured','-updated_at')
        
    @property
    def stripe_curruncy(self):
        return "usd"

    @property
    def stripe_price(self):
        return int(self.price * 100)
           
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id

    def save(self, *args, **kwargs):
        if not self.stripe_id and self.product_stripe_id is not None:
            stripe_id = create_price(
                currency=self.stripe_curruncy,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product_stripe_id=self.product_stripe_id,
                metadata={
                    "subscription_plan_price_id": self.id
                }
            )

            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval
            ).exclude(id=self.id) 
            if qs.exists():
                qs.update(featured=False)
       

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    