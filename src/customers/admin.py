from django.contrib import admin

# Register your models here.

from .models import Customer

admin.site.register(Customer, list_display=["user", "stripe_customer_id", "init_email", "init_email_confirmed"])