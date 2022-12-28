import re
from django.core.validators import RegexValidator

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