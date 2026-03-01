from django.db import models
from restaurants.models import Restaurant
# Create your models here.

    
class Review(models.Model):
    class Source(models.TextChoices):
        GOOGLE = 'Google', 'Google'
        YELP = 'Yelp', 'Yelp'
        TRIPADVISOR = 'TripAdvisor', 'TripAdvisor'
        FACEBOOK = 'Facebook', 'Facebook'
        OTHER = 'Other', 'Other'
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    
    source = models.CharField(max_length=100, default=Source.GOOGLE, choices=Source.choices)

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