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
        if not self.is_valid_subnet(value):
            raise forms.ValidationError('Enter a valid subnet in CIDR notation.')
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

class IPField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def clean_ip_addresses(self):
        ip_addresses = self.cleaned_data['ip_addresses']
        # Clean the list of IP addresses using the clean_ip_list function
        ip_addresses = self.clean_ip_list(ip_addresses)
        # Validate the list of IP addresses using the ip_list_regex regular expression
        #if not ip_list_regex.match(ip_addresses):
        #    raise forms.ValidationError("Invalid list of IP addresses")
        return ip_addresses
    
    def clean_ip_list(self, ip_list):
        # Replace commas and whitespace characters between IP addresses with single spaces
        ip_list = re.sub(r'\s*,\s*', ' ', ip_list)
        # Remove leading and trailing whitespace
        ip_list = ip_list.strip()
        return ip_list

    def clean(self, value):
        super().clean(value)
        # Validate the value of the IP addresses field
        if not value:
            raise forms.ValidationError('This field is required.')
        if not self.is_valid_ip_list(value):
            raise forms.ValidationError('Enter valid comma separated IP addresses.')
        value = self.clean_ip_list(value)
        
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.subnet:
            self.fields['ips_or_subnet'].initial = self.instance.subnet
            self.fields['ips_or_subnet_type'].initial = self.fields['ips_or_subnet_type'].choices[0][0]
        else:
            self.fields['ips_or_subnet'].initial = self.instance.ip_addresses
            self.fields['ips_or_subnet_type'].initial = self.fields['ips_or_subnet_type'].choices[1][0]
