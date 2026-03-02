from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decouple import config
        
class Restaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    
    place_id = models.CharField(max_length=100, null=True, blank=True) 
    name = models.CharField(max_length=100) 
    address = models.CharField(max_length=200, null=True, blank=True) # formatted_address
    phone_number = models.CharField(max_length=20, null=True, blank=True) # international_phone_number
    business_status = models.CharField(max_length=50, null=True, blank=True) 
    
    website = models.URLField(null=True, blank=True) 
    google_maps_url = models.URLField(null=True, blank=True) # url

    delivery = models.BooleanField(null=True, blank=True) 
    dine_in = models.BooleanField(null=True, blank=True) 
    serves_beer = models.BooleanField(null=True, blank=True) 
    serves_wine = models.BooleanField(null=True, blank=True)
    serves_breakfast = models.BooleanField(null=True, blank=True)
    serves_dinner = models.BooleanField(null=True, blank=True)
    serves_lunch = models.BooleanField(null=True, blank=True)
    serves_vegetarian_food = models.BooleanField(null=True, blank=True)
    takeout = models.BooleanField(null=True, blank=True)
    types = models.CharField(max_length=200, null=True, blank=True) 
    wheelchair_accessible_entrance = models.BooleanField(null=True, blank=True)
    reservable = models.BooleanField(null=True, blank=True)
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    price_level = models.IntegerField(null=True, blank=True)
    user_ratings_total = models.IntegerField(null=True, blank=True)
    
    slug = models.SlugField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_list_types(self):
        if self.types:
            return [t.strip() for t in self.types.split(',')]
        return []
    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(" ".join([self.name, self.place_id or ""]))
        super().save(*args, **kwargs)
        
    class Meta:
        unique_together = ('user', 'place_id')
        ordering = ['active', '-created_at']
