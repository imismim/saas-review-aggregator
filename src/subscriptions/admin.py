from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Subscription, UserSubscription, SubscriptionPrice
# Register your models here.

class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice
    extra = 0
    readonly_fields = ('stripe_id',)
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        class SubscriptionPriceForm(formset.form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if self.instance and self.instance.pk:
                    self.fields['interval'].disabled = True
                    self.fields['price'].disabled = True
        
        formset.form = SubscriptionPriceForm
        return formset
  
@admin.register(Subscription)  
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'order', 'count_prices')
    inlines = [SubscriptionPriceInline]
    readonly_fields = ('stripe_id',)
    
    def count_prices(self, obj):
        if obj.subscriptionprice_set.exists():
            return obj.subscriptionprice_set.count()
        return 0
    
    
    count_prices.short_description = 'Number of Prices'
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'view_user_link','view_subscription_link', 'active', 'current_period_start', 'current_period_end')
    readonly_fields = ('stripe_id', 'current_period_start', 'current_period_end')
    list_filter = ('active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'subscription__name')
    
    def view_user_link(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.id])
            return mark_safe(f'<a href="{url}">{obj.user}</a>')
        return "-"
    
    def view_subscription_link(self, obj):
        if obj.subscription:
            url = reverse("admin:subscriptions_subscription_change", args=[obj.subscription.id])
            return mark_safe(f'<a href="{url}">{obj.subscription}</a>')
        return "-"
    
    view_user_link.short_description = 'User Profile'
    view_subscription_link.short_description = 'Subscription'
