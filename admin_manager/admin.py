from django.contrib import admin
from .models import AdminAppointmentApproval, AdminProfile

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = (
        'employee_number', 'user__username', 'full_name', 'user__role',
    )
    search_fields = ('employee_number',)
    list_filter = ('employee_number',)

@admin.register(AdminAppointmentApproval)
class AdminAppointmentApprovalAdmin(admin.ModelAdmin):
    list_display = ('customer_appointment',
                    'assigned_staff', 'approved_time_slot', 'status')
    search_fields = ('customer_appointment__full_name', 'assigned_staff__name')
    list_filter = ('status',)
