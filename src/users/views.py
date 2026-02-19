from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages as message

from subscriptions.models import UserSubscription
from helpers.billing import get_subscription
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
    
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        is_success = refresh_active_users_subscriptions(user_ids=user_id)
        if is_success:
            message.success(request, "Subscription refreshed successfully.")
        else:
            message.error(request, "Failed to refresh subscription.")
            
        return self.get(request, *args, **kwargs)

profile_view = ProfileView.as_view()