
from django.urls import path
from . import views


app_name = 'notifications'

urlpatterns = [

         path('read/<int:pk>/', views.mark_notification_read, name='mark-read'),
        # path('list/', views.get_notifications, name='notification-list'),
]