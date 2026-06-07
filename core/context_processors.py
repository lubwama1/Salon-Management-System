from users.models import CustomUser
from notifications.models import Notification
from site_settings.models import SiteSettings


def user_roles(request):
    if request.user.is_authenticated:
        return {
            'STAFF_ROLE': CustomUser.UserRoleChoices.STAFF,
            'ADMIN_ROLE': CustomUser.UserRoleChoices.ADMIN,
            'CUSTOMER_ROLE': CustomUser.UserRoleChoices.CUSTOMER,
        }
    return {}


def notifications(request):
    if request.user.is_authenticated:

        qs = Notification.objects.filter(
            receiver=request.user
        ).order_by('-timestamp')

        unread_count = qs.filter(is_read=False).count()

        qs.filter(is_read=False).update(is_read=True)
        print(f'UnRead: {unread_count}')

        return {
            'notifications': qs,
            'unread_count': unread_count,
        }

    return {}


def site_settings(request):
    settings = SiteSettings.objects.first()
    if settings:
        return {
            'SITE_NAME': settings.site_name if settings else 'Elite Saloon',
            'SITE_EMAIL': settings.site_email if settings else 'admin@elitesaloon.com',
            'SITE_LOGO': settings.site_logo.url if settings and settings.site_logo else None,
            'SITE_PHONENUMBER': settings.site_phonenumber if settings else '1234567890',
            'SITE_ADDRESS': settings.site_address if settings else 'Hamdan St, Abu Dhabi, UAE',
        }
    return {}
