# Create your models here.
from django.db import models
from django.contrib.auth.models import User

COMPANY_SIZE = (
    ('large', 'LARGE'),
    ('medium', 'MEDIUM'),
    ('small', 'SMALL'),
)

WORK_FIELD = (
    ('real estate', 'Real Estate'),
    ('clothing', 'Clothing'),
    ('construction', 'Construction'),
    ('Installation, repair and maintenance', 'Installation, repair and maintenance'),
)


def productFile(instance, filename):
    return '/'.join(['products', str(instance.id), filename])


def PublicationFile(instance, filename):
    return '/'.join(['publications', str(instance.id), filename])


def ProductImages(instance, filename):
    return '/'.join(['productImages', str(instance.id), filename])


class Publication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name_of_publication = models.CharField(max_length=256, default=0)
    docfile = models.FileField(upload_to=PublicationFile)


class FollowSupplier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='usersupplier')
    following_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='followsupplier')


class Category(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to=productFile, max_length=254, blank=True, null=True)
    company_email = models.CharField(max_length=256, default="", blank=True, null=True)
    company_name = models.CharField(max_length=256, default="")
    trade_role = models.CharField(max_length=256, default="")
    free_trail = models.CharField(max_length=256, default="")
    terms_and_condition = models.TextField(default="")
    website = models.TextField(default="", blank=True, null=True)
    annual_revenue = models.FloatField(default=0.0)
    total_employees = models.IntegerField(default=0)
    location = models.CharField(max_length=256, default="")
    hq_address = models.CharField(max_length=256, default="")
    social_link1 = models.TextField(default="", blank=True, null=True)
    social_link2 = models.TextField(default="", blank=True, null=True)
    company_contact = models.CharField(max_length=256, default="", blank=True, null=True)
    sales_dept_email = models.CharField(max_length=256, default="", blank=True, null=True)
    sales_dept_contact = models.CharField(max_length=256, default="", blank=True, null=True)
    license_no = models.CharField(max_length=256, default="")
    company_size = models.CharField(max_length=256, choices=COMPANY_SIZE, default=0, blank=True, null=True)
    company_type = models.CharField(max_length=256, default="")
    year_of_establishment = models.CharField(max_length=256, default=0)
    user_mobile_number = models.IntegerField(default=0, null=True, blank=True)
    company_brand = models.CharField(max_length=256, default="", blank=True, null=True)
    google_id = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True, blank=True)
    category_name = models.CharField(max_length=256, null=True, blank=True)

    check_login_attempt = models.IntegerField(default=0, blank=True, null=True)
    email_verification_key = models.TextField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    expires_in = models.DateTimeField(null=True, blank=True)

    forgot_password = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    field_of_work = models.CharField(max_length=256, choices=WORK_FIELD, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class Subcategory(models.Model):
    category = models.ForeignKey(Category, related_name="category", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    description = models.TextField()


class ChildSubcategory(models.Model):
    category = models.ForeignKey(Subcategory, related_name="child_category", on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    description = models.TextField()


class AddProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ProductName = models.CharField(max_length=256, null=True, blank=True)
    sku = models.CharField(max_length=256, null=True, blank=True)
    design = models.CharField(max_length=256, null=True, blank=True)
    production = models.CharField(max_length=256, null=True, blank=True)
    budget = models.CharField(max_length=256, null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)


class MultipleImages(models.Model):
    product = models.ForeignKey(AddProducts, on_delete=models.CASCADE, null=True, blank=True, related_name="image")
    image = models.ImageField(upload_to=ProductImages, blank=True, null=True)


class SocialLinks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    linkdin_link = models.CharField(max_length=256, blank=True, null=True)
    facebook_link = models.CharField(max_length=256, blank=True, null=True)
    instagram_link = models.CharField(max_length=256, blank=True, null=True)


class AddServices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    service_name = models.CharField(max_length=256, default="")
    list_skills = models.TextField(null=True, blank=True)
