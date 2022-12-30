from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import Logger
from django.contrib.auth.models import User

 
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log = Logger()
    log.user = User.objects.get(username = user.username)
    log.action = 'login'
    log.result = True
    log.page = request.META.get('HTTP_REFERER')
    log.save()

 
 
@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    log = Logger()
    log.credentials = credentials.get('username')
    log.action = 'login'
    log.result = False
    log.page = request.META.get('HTTP_REFERER')
    log.save()
 
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log = Logger()
    log.user = User.objects.get(username = user.username)
    log.action = 'logout'
    log.result = True
    log.page = request.META.get('HTTP_REFERER')
    log.save()