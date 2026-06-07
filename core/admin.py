from django.contrib import admin
from .models import Contact, TeamMember


class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'message')


admin.site.register(Contact, ContactAdmin)


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'image')
admin.site.register(TeamMember, TeamMemberAdmin)