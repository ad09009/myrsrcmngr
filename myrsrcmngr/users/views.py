from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.urls import reverse_lazy

from .models import Profile

from .owner import OwnerDetailView, OwnerUpdateView, OwnerDeleteView, AddrOwnerUpdateView

from django.utils.translation import gettext_lazy as _

# Create your views here.
class register(SuccessMessageMixin, generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/register.html'
    success_message = _('User %(username)s was created successfully. Log in, please.')

    # the following is an overwritten dispatch method to redirect
    # logged in users away from the registration page
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('website:index')
        return super(register, self).dispatch(request, *args, **kwargs)

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('website:index')

def logout_view(request):
    # Log the user out
    logout(request)

    # Redirect to the login page
    return redirect('website:index')

class ProfileDetailView(OwnerDetailView):
    model = Profile
    fields = '__all__'
    
    # By convention:
    # template_name = "users/profile_detail.html"

class ProfileUpdateView(OwnerUpdateView):
    model = Profile
    fields = ['bio', 'birth_date']
    # template_name = "users/profile_form.html"

class ProfileDeleteView(OwnerDeleteView):
    model = User
    template_name = 'users/profile_confirm_delete.html'
