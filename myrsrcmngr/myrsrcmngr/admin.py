from django.contrib import admin
from website.models import *


admin.site.register(resourcegroups)
admin.site.register(scans)
admin.site.register(services)
admin.site.register(reports)
admin.site.register(hosts)
admin.site.register(changes)
admin.site.register(services_added_removed)
admin.site.register(hosts_added_removed)