# Create your models here.
from django.db import models
from django.contrib.auth.models import User

def productFile(instance, filename):
    return '/'.join( ['products', str(instance.id), filename] )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to=productFile,max_length=254, blank=True, null=True)
    company_email = models.CharField(max_length=256, default="")
    company_name = models.CharField(max_length=256, default="")
    trade_role = models.CharField(max_length=256, default="")
    free_trail = models.CharField(max_length=256, default="")
    terms_and_condition = models.TextField(default="")
    website = models.TextField(default="")
    annual_revenue = models.FloatField(default=0.0)
    total_employees = models.IntegerField(default=0)
    location = models.CharField(max_length=256, default="")
    hq_address = models.CharField(max_length=256, default="")
    social_link1 = models.TextField(default="")
    social_link2 = models.TextField(default="")
    company_contact = models.CharField(max_length=256, default="")
    sales_dept_email = models.CharField(max_length=256, default="")
    sales_dept_contact = models.CharField(max_length=256, default="")
    license_no = models.CharField(max_length=256, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class Category(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name="category", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    description = models.TextField()