from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from datetime import datetime
from .models import scans
from django.http import HttpResponseRedirect

class OwnerCreateView(LoginRequiredMixin, CreateView):

    # Saves the form instance, sets the current object for the view, and redirects to get_success_url().
    def form_valid(self, form):
        object = form.save(commit=False) # don`t commit yet, have to pass the user as owner first
        object.scanAuthor = self.request.user
        object.next_execution_at = datetime.now()
        it = object.save()
        return super(OwnerCreateView, self).form_valid(form)
    
    def get_success_url(self):
           pk = self.object.id
           return reverse_lazy("website:scans-list")
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('website:scans-list')
        return context


class OwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("website:scan-detail", kwargs={"pk": pk})

    def get_queryset(self):
        qs = super(OwnerUpdateView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(scanAuthor=self.request.user) # limit to only modifying their own stuff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('website:scan-detail', kwargs={'pk': self.kwargs['pk']})
        return context

class HostOwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("website:hosts-detail", kwargs={"pk": pk})

    def get_queryset(self):
        qs = super(HostOwnerUpdateView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(resourcegroup__user=self.request.user) # limit to only modifying their own stuff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('website:hosts-detail', kwargs={'pk': self.kwargs['pk']})
        return context

class OwnerDeleteView(LoginRequiredMixin, DeleteView):

    def get_queryset(self):
        qs = super(OwnerDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(scanAuthor=self.request.user)# again, a limit to what they can delete
    
class GroupOwnerCreateView(LoginRequiredMixin, CreateView):

    # Saves the form instance, sets the current object for the view, and redirects to get_success_url().
    def form_valid(self, form):
        object = form.save(commit=False) # don`t commit yet, have to pass the user as owner first
        object.user = self.request.user
        it = object.save()
        return super(GroupOwnerCreateView, self).form_valid(form)
    
    def get_success_url(self):
           pk = self.object.id
           return reverse_lazy("website:groups-list")
       
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('website:groups-list')
        return context

    
class GroupOwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("website:groups-detail", kwargs={"pk": pk})

    def get_queryset(self):
        qs = super(GroupOwnerUpdateView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user) # limit to only modifying their own stuff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('website:groups-detail', kwargs={'pk': self.kwargs['pk']})
        return context


class GroupOwnerDeleteView(LoginRequiredMixin, DeleteView):

    def get_queryset(self):
        qs = super(GroupOwnerDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)# again, a limit to what they can delete
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)