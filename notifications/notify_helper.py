

from .models import Notification

def notify(sender, receiver, message, link, notification_type=Notification.NotificationTypes):
    notification = Notification.objects.create(
        sender=sender,
        receiver=receiver,
        message=message,
        link=link,
        notification_type=notification_type
    )
    return notification