from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from .models import scans

class OwnerCreateView(LoginRequiredMixin, CreateView):

    # Saves the form instance, sets the current object for the view, and redirects to get_success_url().
    def form_valid(self, form):
        object = form.save(commit=False) # don`t commit yet, have to pass the user as owner first
        object.scanAuthor = self.request.user
        schedule = self.request.POST["ScanSchedule"]
        if schedule == 'hh':
            next_at_delta = timedelta(minutes=30)
        elif schedule == 'h':
            next_at_delta = timedelta(hours=1)
        elif schedule == 'd':
            next_at_delta = timedelta(days=1)
        elif schedule == 'w':
            next_at_delta = timedelta(days=7)
        else:
            next_at_delta = timedelta(minutes=15)
        object.next_execution_at = datetime.now() + next_at_delta
        it = object.save()
        return super(OwnerCreateView, self).form_valid(form)
    
    def get_success_url(self):
           pk = self.object.id
           return reverse_lazy("website:index")


class OwnerUpdateView(LoginRequiredMixin, UpdateView):

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("website:scan_detail", kwargs={"pk": pk})

    def get_queryset(self):
        qs = super(OwnerUpdateView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(scanAuthor=self.request.user) # limit to only modifying their own stuff


class OwnerDeleteView(LoginRequiredMixin, DeleteView):

    def get_queryset(self):
        qs = super(OwnerDeleteView, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(scanAuthor=self.request.user)# again, a limit to what they can delete