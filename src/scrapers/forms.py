from django import forms

class AddRestaurantForm(forms.Form):
    PLATFORM_CHOICES = [
        ('google', 'Google Maps'),
        ('tripadvisor', 'TripAdvisor'),
    ]
    platform = forms.ChoiceField(choices=PLATFORM_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.google.com/maps/place/...'
        }),
        help_text="Paste the direct link to the restaurant's review page."
    )