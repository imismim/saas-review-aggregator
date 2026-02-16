from django.contrib import admin
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
    
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    inlines = [SubscriptionPriceInline]
    readonly_fields = ('stripe_id',)
    

admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(UserSubscription, list_display=('user', 'subscription', 'active', 'created_at', 'updated_at'))
