
import os


def staff_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if hasattr(instance, 'user') and instance.user:
        username = instance.user.username.lower()
    elif hasattr(instance, 'username'):
        username = instance.username.lower()
    else:
        username = f'staff_{instance.pk or "unknown"}'
    return os.path.join('staff_profiles/', f"{username}.{ext}")
