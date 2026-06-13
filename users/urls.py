
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.UserRegistrationView.as_view(), name='account_signup'),
    path('login/', views.UserLoginView.as_view(), name='account_login'),
    path('logout/', views.user_logout, name='account_logout'),
    path('staff-register-confirmation/', views.staff_register_confirmation,
         name='staff-confirmation'),
    path('admin-register-confirmation/',
         views.admin_register_confirmation, name='admin-confirmation'),
]
