
import os


def customer_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    if hasattr(instance, 'user') and instance.user:
        username = instance.user.username.lower()
    elif hasattr(instance, 'username'):
        username = instance.username.lower()
    else:
        username = f'customer_{instance.pk or "unknown"}'
    return os.path.join('customer_profiles/', f'{username}.{ext}')