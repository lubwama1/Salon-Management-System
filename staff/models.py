from django.db import models
from django.utils import timezone
from django.conf import settings
from .utils import staff_profile_image_path
from django.utils.text import slugify

class StaffProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    employee_number = models.CharField(
        max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(
        upload_to=staff_profile_image_path, blank=True, null=True, default='default.jpg')
    date_of_birth = models.DateField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    ROLE_CHOICES = (
        ('hair stylist', 'Hair Stylist'),
        ('receptionist', 'Receptionist'),
        ('manager', 'Manager'),
        ('massage therapist', 'Massage Therapist'),
        ('nail technician', 'Nail Technician'),
        ('esthetician', 'Esthetician'),
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='N/A')
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} ({self.role})"

    # def save(self, *args, **kwargs):
    #     if not self.employee_number:
    #         self.employee_number = self.generate_employee_number()
    #     super().save(*args, **kwargs)

    def generate_employee_number(self):
        """
        Generates a unique employee number like 'EMP001', 'EMP002', etc.
        """

        prefix = 'ELS'
        last_staff = StaffProfile.objects.order_by('id').last()
        if last_staff and last_staff.employee_number:
            last_number = int(last_staff.employee_number.replace(prefix, ''))
            new_number = last_number + 1
        else:
            new_number = 1
        return f'{prefix}{new_number:03d}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username if self.user else self.full_name)
            slug = base_slug
            counter = 1
            while StaffProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
