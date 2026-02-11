from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .forms import AddRestaurantForm

# Create your views here.

class HomeView(View):
    
    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            form = AddRestaurantForm()
            return render(request, 'scrapers/paste_url.html', {'form': form})
        return render(request, 'scrapers/start_page.html')



home_view = HomeView.as_view()