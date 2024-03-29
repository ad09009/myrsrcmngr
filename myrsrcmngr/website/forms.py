from .custom_validators import *
from django import forms
from .models import resourcegroups
from django.core.exceptions import ValidationError

class SubnetField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, value):
        super().clean(value)
        # Validate the value of the subnet field
        if not value:
            raise forms.ValidationError('This field is required.')
        if not (self.is_valid_subnet(value) or not self.is_valid_ip_list(value)):
            raise forms.ValidationError('Enter a valid subnet in CIDR notation or valid IPv4 list (comma separated).')
            
        return value

    def is_valid_subnet(self, value):
        # Validation logic for the subnet field
        # Return True if the value is a valid subnet, False otherwise
        # If the subnet field is not empty, validate that it is a valid CIDR notation
        if value:
            try:
                validate_cidr(value)
            except ValidationError:
                raise ValidationError("Please enter a valid CIDR notation for the subnet.")
        return value
    
    def is_valid_ip_list(self, value):
        # Validation logic for the IP addresses field
        # Return True if the value is a valid list of IP addresses, False otherwise
        # If the IP addresses field is not empty, validate that it contains a list of valid IP addresses in the correct format
        if value:
            # Validate the IP addresses field using the ip_list_regex RegexValidator
            try:
                validate_ip_list(value)
            except ValidationError:
                raise ValidationError("Please enter a valid list of IP addresses in the correct format (comma separated).")
        return value


class GroupsForm(forms.ModelForm):
    IPS_OR_SUBNET_CHOICES = [
        ('subnet', 'Subnet'),
        ('ip_addresses', 'IP Addresses'),
    ]
    ips_or_subnet_type = forms.ChoiceField(choices=IPS_OR_SUBNET_CHOICES, label="Choose IPs or subnet", widget=forms.RadioSelect)
    ips_or_subnet = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter IPs or subnet'}), label="")

    class Meta:
        model = resourcegroups
        fields = ['subnet', 'ip_addresses', 'name','description']

    def clean(self):
        cleaned_data = super().clean()
        ips_or_subnet_type = cleaned_data.get('ips_or_subnet_type')
        ips_or_subnet = cleaned_data.get('ips_or_subnet')

        if ips_or_subnet_type == 'subnet':
            # Validate the subnet field
            subnet_field = SubnetField()
            cleaned_data['subnet'] = subnet_field.clean(ips_or_subnet)
            # Set the IP addresses field to an empty string
            cleaned_data['ip_addresses'] = ''
        elif ips_or_subnet_type == 'ip_addresses':
            # Validate the IP addresses field
            ip_field = IPField()
            cleaned_data['ip_addresses'] = ip_field.clean(ips_or_subnet)
            # Set the subnet field to an empty string
            cleaned_data['subnet'] = ''
        else:
            raise forms.ValidationError('Invalid choice.')

        return cleaned_data
