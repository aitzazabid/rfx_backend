from django.db import models
from django.contrib.auth.models import User
# Create your models here.
ENTITY_STATUS_CHOICES = (
    ('client', 'Client'),
    ('supplier', 'Supplier'),
    ('other', 'Other'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip = models.CharField(max_length=5)
    types = models.CharField(max_length=20,choices=ENTITY_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
