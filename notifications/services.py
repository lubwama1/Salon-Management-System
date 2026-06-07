# notifications/services.py

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification(notification):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{notification.receiver.id}",
        {
            "type": "notification_message",
            "sender": notification.sender.role if notification.sender else "None",
            "notification_id": notification.id,
            "sender": notification.sender.username,
            "message": notification.message,
            "link": notification.link,
            "notification_type": notification.notification_type,
            "unread_count": notification.receiver.received_notifications.filter(is_read=False).count(),
            "timestamp": notification.timestamp.isoformat(),
        }
    )
