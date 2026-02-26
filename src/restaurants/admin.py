from django.contrib import admin
from .models import Platform, Restaurant, Review

# Register your models here.

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'active')
    search_fields = ('name', 'city', 'country')
    list_filter = ('active',)
    ordering = ('-created_at',)
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'source', 'author', 'rating')
    search_fields = ('restaurant__name', 'author')
    list_filter = ('source', 'restaurant')
    ordering = ('-review_date',)