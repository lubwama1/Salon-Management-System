from django.contrib import admin
from .models import SiteSettings


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_email',
                    'site_phonenumber', 'site_address')
    search_fields = ('site_name', 'site_email')


admin.site.register(SiteSettings, SiteSettingsAdmin)
