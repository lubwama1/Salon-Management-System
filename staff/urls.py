
from . import views

from django.urls import path

app_name = 'staff'

urlpatterns = [
    path('profile/', views.StaffProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditStaffProfileView.as_view(), name='profile-edit'),

    path('appointments/', views.StaffScheduleView.as_view(), name='appointments'),
    path('appointments/history/', views.StaffAppointmentHistoryView.as_view(),
         name='appointments-history'),

    path('notifications/', views.NotificationView.as_view(), name='notifications'),
    path('notifications/delete-selected/', views.delete_selected_notification,
         name='delete-selected-notifications'),
    path('notifications/delete-all/', views.delete_all_notifications,
         name='delete-all-notifications'),
]
