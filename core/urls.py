from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),
    # About
    path('about-us/', views.AboutView.as_view(), name='about-us'),
    # Contact
    path('contact/', views.contact_us, name='contact'),
    # Privacy Policy
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
]
