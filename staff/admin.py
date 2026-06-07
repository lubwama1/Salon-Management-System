from django.contrib import admin
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'role')
    search_fields = ('full_name', 'email', 'role')
    list_filter = ('role',)
