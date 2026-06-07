from django.db import models
from services.models import Service
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5, validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.service.name}'
