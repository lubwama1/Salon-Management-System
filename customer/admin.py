from django.contrib import admin
from .models import CustomerAppointment

@admin.register(CustomerAppointment)
class CustomerAppointmentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'service', 'appointment_date', 'status')
    search_fields = ('full_name', 'email', 'phone_number', 'service__name')
    list_filter = ('appointment_date',)