from django.db import models
from datetime import date

class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.full_name


class TeamMember(models.Model):
    class TeamCategory(models.TextChoices):
        FOUNDER = 'founder', 'Founder & CEO'
        SUPPORT = 'support', 'Support Staff'
        SENIOR = 'head_stylist', 'Head Stylist'

    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=TeamCategory.choices, default='Staff')
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='team/', default='default.jpg')
    email = models.EmailField(blank=True)
    years_of_experience = models.DateField()

    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    github = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name

    @property
    def experience_years(self):
        return date.today().year - self.years_of_experience.year