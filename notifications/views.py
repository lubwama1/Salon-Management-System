from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Notification


def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, id=pk)
    if not notification.is_read:
        notification.mark_as_read()
    return redirect(notification.link if notification.link else 'core:home')


def get_notifications(request):
    notifications = Notification.objects.filter(
        receiver=request.user).order_by('-timestamp')
    data = []
    unread_count = notifications.filter(is_read=False).count()
    # print(Notification.objects.all())
    # print(notifications)
    for n in notifications:
        data.append({
            'id': n.id,
            'sender': n.sender.username,
            'message': n.message,
            'url': n.link,
            'notification_type': n.notification_type,
            'is_read': n.is_read,
            'timestamp': n.timestamp.isoformat(),
        })
    # print(
    #     f"Fetched {len(data)} notifications for user {request.user.username}, Unread count: {unread_count}\n{data}")
    return JsonResponse({'notifications': data, 'unread_count': unread_count})
