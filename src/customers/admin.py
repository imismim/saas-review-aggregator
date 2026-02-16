from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
# Register your models here.

from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('stripe_id', 'view_user_link', 'init_email', 'init_email_confirmed')
    search_fields = ('user__username', 'stripe_id', 'init_email')
    
    def view_user_link(self, obj):
        if obj.user:
            url = reverse("admin:auth_user_change", args=[obj.user.id])
            return mark_safe(f'<a href="{url}">{obj.user}</a>')
        return "-"

    view_user_link.short_description = 'User'
    