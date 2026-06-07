from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [

    # ================= BOOKINGS =================
    path('booking/', views.BookingView.as_view(), name='booking'),
    path('booking/service/<slug:service_slug>/',
         views.BookingView.as_view(), name='booking-with-service'),

    # ================= APPOINTMENTS =================
    path('appointments/', views.AppointmentHistoryView.as_view(),
         name='appointment-list'),
    path('appointments/confirmation/', views.AppointmentConfirmationView.as_view(),
         name='appointment-confirmation'),
    path('appointments/<int:appointment_id>/resubmit/',
         views.ResubmitAppointmentView.as_view(), name='appointment-resubmit'),
    path('appointments/<int:appointment_id>/cancel/',
         views.costumer_cancel_appointment, name='appointment-cancel'),

    # ================= PROFILE =================
    path('profile/', views.CustomerProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='profile-edit'),


    # ================= NOTIFICATIONS =================
    path('notifications/delete-selected/', views.delete_selected_notification,
         name='delete-selected-notifications'),
    path('notifications/', views.NotificationView.as_view(), name='notifications'),
    path('notifications/delete-all/', views.delete_all_notifications,
         name='delete-all-notifications'),
]
