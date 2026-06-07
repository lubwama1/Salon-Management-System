

from django.urls import path
from . import views

app_name = 'admin_manager'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ================= STAFF =================
    path('staff/', views.StaffManagementView.as_view(), name='staff-list'),
    path('staff/add/', views.AddStaffView.as_view(), name='staff-add'),
    path('staff/<slug:staff_slug>/',
         views.StaffProfileAdminView.as_view(), name='staff-detail'),
    path('staff/<slug:staff_slug>/edit/',
         views.EditStaffProfileAdminView.as_view(), name='staff-edit'),
    path('staff/<slug:staff_slug>/delete/',
         views.DeleteStaffAdminView.as_view(), name='staff-delete'),
    path('staff/search', views.filter_staff, name='staff-search'),

    # ================= CUSTOMERS =================
    path('customers/', views.CustomerManagementView.as_view(), name='customer-list'),
    path('customers/<int:customer_id>/',
         views.CustomerProfileAdminView.as_view(), name='customer-detail'),
    path('customers/<int:customer_id>/edit/',
         views.CustomerEditProfileAdminView.as_view(), name='customer-edit'),
    path('customers/<int:customer_id>/delete/',
         views.CustomerDeleteAdminView.as_view(), name='customer-delete'),

    # ================= APPOINTMENTS =================
    path('appointments/<int:approval_id>/review/',
         views.admin_appointment_review, name='appointment-review'),
    path('appointments/<int:appointment_id>/cancel/',
         views.admin_cancel_appointment, name='appointment-cancel'),

    # ================= ADMIN PROFILE =================
    path('profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    path('profile/edit/', views.EditAdminProfileFormView.as_view(),
         name='admin-profile-edit'),
    # ================= NOTIFICATIONS =================
    path('notifications/', views.NotificationView.as_view(),
         name='notifications'),
    path('notifications/appointments', views.AppointmentNotificationView.as_view(),
         name='notifications-appointment'),
    path('notifications/delete-selected/',
         views.delete_selected_notification, name='delete-selected-notifications'),
    path('notifications/delete-all/',
         views.delete_all_notifications, name='delete-all-notifications'),

    # ================= REVIEWS =================
    path('feedback/reviews/', views.customer_reviews, name='reviews'),
    path('feedback/<int:review_id>/update-approval/',
         views.update_approval, name='update-approval'),
    path('feedback/<int:pk>/delete/',
         views.DeleteReviewView.as_view(), name='review-delete'),

    # ================= BACKUP SYSTEM =================
    path(
        'backup/system/', views.system_backup_page, name='system-backup-page'
    ),
    path('backup/<str:format>/system/',
         views.system_backup, name='system-backup'),

    # ================= Team Members =================
    path('team/member/create/', views.AddTeamMemberView.as_view(), name='add-member'),
    path('team/list/', views.TeamMemberView.as_view(), name='team-list'),
    path('team/member/<int:member_id>/delete/',
         views.delete_team_member, name='delete-member'),
    path('team/member/<int:member_id>/edit/',
         views.TeamMemberEditView.as_view(), name='edit-member'),
]
