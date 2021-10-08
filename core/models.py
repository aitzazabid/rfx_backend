from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .customUserManager import CustomUserManager
# Create your models here.
ENTITY_STATUS_CHOICES = (
    ('client', 'Client'),
    ('supplier', 'Supplier'),
    ('other', 'Other'),
)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    trade_role = models.CharField(max_length=256, default="")
    free_trail = models.CharField(max_length=256, default="")
    terms_and_condition = models.TextField(default="")
    website = models.TextField(default="")
    annual_revenue = models.FloatField(default=0.0)
    total_employees = models.IntegerField(default=0)
    location = models.CharField(max_length=256, default="")
    hq_address = models.CharField(max_length=256, default="")
    socialLink = models.TextField(default="")
    company_contact = models.CharField(max_length=256, default="")
    sales_dept_email = models.CharField(max_length=256, default="")
    sales_dept_contact = models.CharField(max_length=256, default="")
    license_no = models.CharField(max_length=256, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
