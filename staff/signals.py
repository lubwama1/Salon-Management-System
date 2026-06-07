
from django.dispatch import receiver
from users.models import CustomUser
from django.db.models.signals import post_save
from .models import StaffProfile


@receiver(post_save, sender=CustomUser)
def create_staff_profile(sender, created, instance, **kwargs):
    if created and instance.role == 'staff':
        StaffProfile.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def save_staff_profile(sender, instance, **kwargs):
#     if instance.role == 'staff':
#         if hasattr(instance, 'staffprofile'):
#             instance.staffprofile.save()
