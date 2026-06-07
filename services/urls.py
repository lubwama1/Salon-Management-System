
from django.urls import path
from . import views

app_name = 'services'



urlpatterns = [

    # ================= SERVICES =================
    path('service-list/', views.ServiceListView.as_view(), name='service-list'),

    path('service/<slug:category_slug>/',
         views.ServiceDetailView.as_view(), name='service-detail'),

    path('service/<slug:category_slug>/add/',
         views.AddServiceView.as_view(), name='service-add'),

    path('service/<slug:service_slug>/edit/',
         views.EditServiceView.as_view(), name='service-edit'),

    path('service/<slug:service_slug>/delete/',
         views.DeleteServiceView.as_view(), name='service-delete'),

    # ================= CATEGORIES =================
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    path('categories/add/', views.AddServiceCategoryView.as_view(),
         name='category-add'),

    path('categories/<slug:category_slug>/edit/',
         views.EditCategoryView.as_view(), name='category-edit'),

    path('categories/<slug:category_slug>/delete/',
         views.DeleteCategoryView.as_view(), name='category-delete'),

    path('category/<slug:category_slug>/',
         views.ServiceListView.as_view(),
         name='service-by-category'),
]