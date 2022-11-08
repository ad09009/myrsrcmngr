from django.db import models

class Resource(models.Model):
    add_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    def __str__(self):
        return self.name
    