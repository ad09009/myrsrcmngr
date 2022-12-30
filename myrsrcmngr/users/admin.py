from django.contrib import admin

from .models import Profile, Logger
# Register your models here.



# Register your models here.
class LoggerAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'created_at',
                    'action',
                    'result',
                    'credentials',
                    'page'
                    ]
    list_display_links = [
        'user',
    ]
    list_filter = ['user',
                   'result',
                   'action'
                   ]
    search_fields = [
        'user__username'
    ]

admin.site.register(Profile)
admin.site.register(Logger, LoggerAdmin)