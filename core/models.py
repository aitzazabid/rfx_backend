from django.db import models
from django.contrib.auth.models import User
# Create your models here.
ENTITY_STATUS_CHOICES = (
    (0, 'Pending'),
    (1, 'Active'),
    (2, 'Inactive'),
    (3, 'Hold'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile',
                                on_delete=models.CASCADE)
    status = models.IntegerField(default=1, choices=ENTITY_STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
