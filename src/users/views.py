from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from subscriptions.models import UserSubscription
from helpers.billing import get_subscription
# Create your views here.


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_subscriptions, created = UserSubscription.objects.get_or_create(user=user)
        from pprint import pprint
        pprint(user_subscriptions.serialize())
        context['sub_data'] = user_subscriptions.serialize()

        return context
    
    def post(self, request, *args, **kwargs):
        print("refreshing subscription status")
        context = self.get_context_data(**kwargs)   
        sub_data = context.get('sub_data')
        stripe_id = sub_data.get('stripe_id')
        if stripe_id:
            refresh_user_sub_data = get_subscription(stripe_id, raw=False)
            user_sub_obj, created = UserSubscription.objects.get_or_create(stripe_id=stripe_id)
            for k, v in refresh_user_sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
        return self.get(request, *args, **kwargs)

profile_view = ProfileView.as_view()