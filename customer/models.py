from django.db import models
from services.models import Service
from django.conf import settings
from .utils import customer_profile_image_path
from feedback.models import Feedback

class CustomerAppointment(models.Model):
    # APPOINTMENT_STATUS_CHOICES = (
    #     ('pending', 'Pending'),
    #     ('confirmed', 'Confirmed'),
    #     ('canceled', 'Cancelled'),
    # )
    class AppointmentStatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending (awaiting confirmation)'
        APPROVED = 'approved', 'Approved & confirm booking'
        REJECTED = 'rejected', 'Rejected Appointment / Decline'
        CANCELED = 'canceled', 'Canceled by Customer'
        COMPLETED = 'completed', 'Completed Appointment'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_appointments')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    time_slot = models.TimeField()
    status = models.CharField(
        max_length=20, choices=AppointmentStatusChoices.choices, default=AppointmentStatusChoices.PENDING)
    profile_picture = models.ImageField(
        upload_to=customer_profile_image_path, blank=True, null=True, default='default_profile.jpg')

    def __str__(self):
        return f"{self.service} on {self.appointment_date} at {self.time_slot} - {self.status}"

    @property
    def customer_profile_image(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/media/default_profile.jpg'

    def get_user_review(self):
        try:
            return Feedback.objects.get(
                user=self.user,
                service=self.service,
                approved=True
            )
        except Feedback.DoesNotExist:
            return None

