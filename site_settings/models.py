from django.db import models
from django.core.exceptions import ValidationError


class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=100,
        default="Elite Saloon",
        help_text="The name of your business/site"
    )
    site_email = models.EmailField(
        default="admin@elitesaloon.com",
        help_text="Primary contact email"
    )
    site_logo = models.ImageField(
        upload_to='site_logo/',
        blank=True,
        null=True,
        help_text="Upload your site logo (recommended size: 200x200px)"
    )
    site_phonenumber = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        default="1234567890",
        help_text="Contact phone number"
    )
    site_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="Hamdan St, Abu Dhabi, UAE",
        help_text="Physical address"
    )
    site_description = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of your business"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def clean(self):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(
                'Only one SiteSettings instance can exist. '
                'Please edit the existing one instead.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure clean() is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.site_name} Settings'
