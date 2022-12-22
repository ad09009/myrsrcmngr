from .custom_validators import *
from django import forms
from .models import resourcegroups


class SubnetField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_cidr)

class GroupsForm(forms.ModelForm):
    subnet = SubnetField()

    class Meta:
        model = resourcegroups
        fields = ['name','description','subnet']