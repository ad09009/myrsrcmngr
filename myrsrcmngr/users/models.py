from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

#from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    userfor = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField("Role", max_length=400, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    #userlikes = models.ManyToManyField("FoodType", blank=True)

    def __str__(self):
        return str(self.userfor)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(userfor=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Logger(models.Model):
    class Meta:
        verbose_name_plural = "Loggers"
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    credentials = models.CharField(null = True, blank = True, max_length=50)
    action = models.CharField(max_length=20)
    page = models.CharField(max_length=60, null = True, blank = True)
    result = models.BooleanField(default = True)