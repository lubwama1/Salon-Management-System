

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from services.models import Service, ServiceCategory

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'
    def items(self):
        return ['core:home', 'core:about-us', 'core:contact',]
    def location(self, item):
        return reverse(item)

class ServiceViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'
    def items(self):
        return Service.objects.all()
    # def location(self, item):
    #     return reverse('services:service_detail', kwargs={'pk': item.pk})
    def lastmod(self, obj):
        return obj.updated_at

class CategoryViewSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'
    def items(self):
        return ServiceCategory.objects.all()
    # def location(self, item):
    #     return reverse('services:service_category', kwargs={'category': item})
    def lastmod(self, obj):
        return obj.updated_at