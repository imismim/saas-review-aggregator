from django.contrib import admin
from .models import Subscription, UserSubscription, SubscriptionPrice
# Register your models here.

class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice
    extra = 0
    readonly_fields = ('stripe_id',)
    can_delete = False

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    inlines = [SubscriptionPriceInline]
    readonly_fields = ('stripe_id',)
    

admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(UserSubscription, list_display=('user', 'subscription', 'active', 'created_at', 'updated_at'))
