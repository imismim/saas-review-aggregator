from django import forms
from .models import Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'name',
            'cuisine_type',
            'description',
            'address',
            'city',
            'country',
            'phone_number',
            'email',
            'website',
            'tripadvisor_url',
            'active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant name'}),
            'cuisine_type': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555 000 0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@restaurant.com'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'tripadvisor_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tripadvisor.com/...'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
