from .custom_validators import *
from django import forms
from .models import resourcegroups


class SubnetField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(validate_cidr)

class IPField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(ip_list_regex, 'Enter a valid list of IPv4 addresses', 'invalid'))

class GroupsForm(forms.ModelForm):
    subnet = SubnetField()
    ip_addresses = IPField()
    
    IPS_OR_SUBNET_CHOICES = [
        ('subnet', 'Subnet'),
        ('ip_addresses', 'IP Addresses'),
    ]
    ips_or_subnet_type = forms.ChoiceField(choices=IPS_OR_SUBNET_CHOICES)
    ips_or_subnet = forms.CharField(required=True)
    
    class Meta:
        model = resourcegroups
        fields = ['name','description','subnet', 'ip_addresses']
        
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
    
    def clean(self):
        cleaned_data = super().clean()
        ips_or_subnet_type = cleaned_data.get('ips_or_subnet_type')
        ips_or_subnet = cleaned_data.get('ips_or_subnet')

        if ips_or_subnet_type == 'subnet':
            # Validate the subnet field
            pass
        elif ips_or_subnet_type == 'ip_addresses':
            # Validate the IP addresses field
            pass

        return cleaned_data