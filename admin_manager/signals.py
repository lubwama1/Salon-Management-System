
from django.dispatch import receiver
from django.db.models.signals import post_save
from admin_manager.models import AdminProfile
from users.models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_admin_profile(sender, created, instance, **kwargs):
    if created and instance.role == 'admin':
        AdminProfile.objects.create(user=instance)


# @receiver(post_save, sender=CustomUser)
# def save_admin_profile(sender, instance, **kwargs):
#     if instance.role == 'admin':
#         if hasattr(instance, 'adminprofile'):
#             instance.adminprofile.save()
