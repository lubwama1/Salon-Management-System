from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class UserRoleChoices(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin Manager'
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(
        upload_to='user_pictures/', blank=True, null=True, default='default.jpg')
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=10, choices=UserRoleChoices.choices, default=UserRoleChoices.CUSTOMER)
    date_of_birth = models.DateField(blank=True, null=True)
    is_staff_verified = models.BooleanField(default=False)
    is_admin_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        if self.role == self.UserRoleChoices.STAFF and not self.is_staff_verified:
            return f"{self.username} (Unverified Staff)"
        return f"{self.username} ({self.role})"
