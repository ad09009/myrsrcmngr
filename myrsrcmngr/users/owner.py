
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages

from website.models import resourcegroups

from django.utils.translation import gettext_lazy as _

class OwnerDetailView(LoginRequiredMixin, DetailView):
    """
    Sub-class of the DetailView for passing the request to the form.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rec = resourcegroups.objects.filter(RecipeAuthor = self.object.userfor)
        context['rec'] = rec
        return context

class OwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("users:profile-home", kwargs={"pk": pk})

    def get_queryset(self):
        qs = super(OwnerUpdateView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(userfor=self.request.user)# limit to only modifying their own stuff


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_success_url(self):
        text = _('Your profile was deleted. Sad to see you go!')
        messages.success(self.request, text)
        return reverse_lazy("receptes:receptes-home")
    
    def get_queryset(self):
        qs = super(OwnerDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(username=self.request.user)# again, a limit to what they can delete

class AddrOwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           return self.request.POST.get('next')

    def get_queryset(self):
        qs = super(AddrOwnerUpdateView, self).get_queryset()
        return qs.filter(userlives__profile_who=self.request.user.profile)