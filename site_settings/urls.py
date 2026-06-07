
from django.urls import path
from . import views

app_name = 'site_settings'

urlpatterns = [
    path('', views.SiteSettingsView.as_view(), name='settings'),
    path('create/', views.SiteSettingsCreateView.as_view(),
         name='create_settings'),
    path('update/', views.SiteSettingsUpdateView.as_view(),
         name='update_settings'),
]
