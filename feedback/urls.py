
from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('reviews/', views.ReviewView.as_view(), name='review'),
    path('services/<slug:service_slug>/reviews/',
         views.ServiceReviewView.as_view(), name='service-reviews'),
    path(
        'service/<slug:service_slug>/review/',
        views.CreateReviewView.as_view(),
        name='create-review'
    ),

]
