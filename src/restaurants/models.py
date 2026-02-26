from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decouple import config

class Platform(models.Model):
    name = models.CharField(max_length=100)          
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    
class Restaurant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    cuisine_type = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    tripadvisor_url = models.URLField(null=True, blank=True)
    
    slug = models.SlugField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-created_at']
        
class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    
    source = models.ForeignKey(Platform, on_delete=models.SET_NULL, null=True)
 
    author = models.CharField(max_length=100, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:  
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.source} - {self.restaurant.name} - {self.rating}"