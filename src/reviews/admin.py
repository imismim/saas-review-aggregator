from django.contrib import admin
from .models import Review

# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'source', 'author', 'rating', 'review_date')
    list_filter = ('source', 'review_date')
    search_fields = ('restaurant__name', 'author', 'text')