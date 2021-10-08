# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=256, default="")
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
