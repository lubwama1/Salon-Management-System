from django.test import TestCase
from .models import Service

class ServiceModelTest(TestCase):
    def test_service_creation(self):
        service = Service.objects.create(
            name='Hair Cut',
            price=50
        )
        self.assertEqual(service.name, 'Hair Cut')
        self.assertEqual(service.price, 50)