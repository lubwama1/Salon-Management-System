
from django.db import models
from django.conf import settings
# from services.models import Service
from customer.models import CustomerAppointment
from django.utils import timezone
# from django.utils.crypto import get_random_string
from staff.models import StaffProfile
from .utils import admin_profile_image_path
from django.conf import settings


class AdminAppointmentApproval(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELED = 'canceled', 'Canceled'
        COMPLETED = 'completed', 'Completed'
    # STATUS_CHOICES = (
    #     ('pending', 'Pending'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    # )

    class CANCELLED_REASON(models.TextChoices):
        # Customer reasons
        CUSTOMER_REQUEST = 'customer_request', 'Customer Request'
        BUSY_SCHEDULE = 'busy_schedule', 'Busy Schedule'
        FOUND_ANOTHER = 'found_another', 'Found Another Service Provider'
        OTHER = 'other', 'Other Reason'

        # Admin reasons
        ADMIN_CANCELLED = 'admin_cancelled', 'Admin Cancelled'
        NO_SHOW = 'no_show', 'Client did not show up'

    customer_appointment = models.OneToOneField(
        CustomerAppointment, on_delete=models.CASCADE, related_name='admin_approval')
    assigned_staff = models.ForeignKey(
        StaffProfile, on_delete=models.SET_NULL, null=True)
    approved_time_slot = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_canceled_appointments')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(
        max_length=50, choices=CANCELLED_REASON.choices, blank=True, null=True)

    def __str__(self):
        return f"Appointment for {self.customer_appointment.full_name} - {self.status}"

    def get_cancellation_reason_display_text(self):
        if self.cancellation_reason:
            return self.get_cancellation_reason_display()
        return "N/A"
class AdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    employee_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200, default='N/A')
    phone_number = models.CharField(max_length=20, blank=True)
    admin_profile_image = models.ImageField(
        upload_to=admin_profile_image_path, default='default_profile.jpg')

    def __str__(self):
        return f"'{self.user.username}'s profile - {self.user.role}"

    def save(self, *args, **kwargs):
        if not self.employee_number:
            self.employee_number = self.generate_admin_employee_number()
        super().save(*args, **kwargs)

    def generate_admin_employee_number(self):
        """
        Generates a unique ADMIN employee number like 'ELSA001', 'ELSA002', etc.
        """

        prefix = 'ELSA'
        last_admin = AdminProfile.objects.order_by('id').first()
        if last_admin and last_admin.employee_number:
            last_number = int(last_admin.employee_number.replace(prefix, ''))
            new_number = last_number + 1
        else:
            new_number = 1
        return f'{prefix}{new_number:03d}'
