from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    class NotificationTypes(models.TextChoices):
        APPOINTMENT = 'appointment', 'Appointment'
        CANCELED_APPOINTMENT = 'canceled_appointment', 'Canceled Appointment'
        ASSIGNED_STAFF = 'assigned_staff', 'Assigned Staff'
        SYSTEM = 'system', 'SYSTEM'
        APPROVED = 'approved', 'Approved Appointment'
        REJECTED = 'rejected', 'Rejected'
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='received_notifications'
    )
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50, choices=NotificationTypes.choices, default=NotificationTypes.SYSTEM
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )
    link = models.URLField(
        blank=True, null=True,
        help_text='Optional link to redirect(e.g., appointments)'
    )
    is_read = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Notifications'

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def __str__(self):
        return f'SENDER: {self.sender} -> RECEIVER: {self.receiver} TYPE: ({self.notification_type})'
