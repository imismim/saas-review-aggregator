from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages as message
from django.shortcuts import redirect
from django.urls import reverse

from subscriptions.models import UserSubscription
from subscriptions.utils import refresh_active_users_subscriptions
# Create your views here.


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_subscriptions, created = UserSubscription.objects.get_or_create(user=user)

        context['sub_data'] = user_subscriptions.serialize() if user_subscriptions.stripe_id else None
        return context
    

profile_view = ProfileView.as_view()

