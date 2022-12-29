import re
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

cidr_regex = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$')
validate_cidr = RegexValidator(cidr_regex, 'Enter a valid subnet in CIDR notation', 'invalid')

ip_list_regex = re.compile(r'^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(,\s*))*(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
validate_ip_list = RegexValidator(ip_list_regex, 'Enter a valid comma separated list of IPv4 addresses', 'invalid')

def listify(string):
    str = string.split(",")
    str = [x.strip() for x in str]
    return str

def is_subnet(string):
    if cidr_regex.match(string):
        return True
    else:
        return False
    
def validate_ips_or_subnet(value):
    if not re.match(cidr_regex, value) and not re.match(ip_list_regex, value):
        raise ValidationError('Value must be a valid subnet or a list of comma-separated IP addresses')