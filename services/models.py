from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=100, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            base_slug = slugify(self.name)
            slug = base_slug
            # Make unique
            counter = 1
            while ServiceCategory.objects.filter(slug=self.slug).exists():
                slug = f"{slugify(base_slug)}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('services:service-by-category', kwargs={'category_slug': self.slug})
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"
        verbose_name = "Service Category"

class Service(models.Model):
    service_category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name='services', null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == '':
            base_slug = slugify(self.name)
            slug = base_slug
            # self.slug = slugify(self.name)
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{slugify(base_slug)}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('services:service-detail', kwargs={'category_slug': self.slug})
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Services"
        verbose_name = "Service"