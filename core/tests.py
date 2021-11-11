from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import UserProfile
import json
from datetime import timedelta
from django.utils import timezone


# Create your tests here.
class RegistrationTestCase(APITestCase):

    def setUp(self):
        self.credentials = {
            'username':'testuser12@gmail.com',
            'email':'testuser12@gmail.com',
            'password': 'secret',
            'first_name':'ali1',
            'last_name':'usman',
        }
        self.u1 = User.objects.create_user(**self.credentials)
        self.u2 = UserProfile.objects.create(user=self.u1)

    def test_create_account(self):
        data = {
            "first_name": "ali",
            "email": "haider120987@gmail.com",
            "password": "abc123456",
            "company_name": "aitzaz987210",
            "trade_role": "traderole201",
            "free_trail": "free_trail1243",
            "terms_and_condition": "terms12356",
            "website": "web1",
            "annual_revenue": 10.5,
            "total_employees": 10,
            "location": "loc1",
            "hq_address": "h1_add",
            "socialLink1": "socialLink1",
            "socialLink2": "socialLink2",
            "company_contact": "companY_con1",
            "sales_dept_email": "sales1",
            "sales_dept_contact": "sales2",
            "license_no": "CHR123",
            "expires_in": timezone.now() + timedelta(days=3)
        }
        response = self.client.post("/signup", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        import pdb; pdb.set_trace()
        response = self.client.post("/login/", self.credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_update_post(self):
        self.valid_post = {
            'username': 'testuser1212@gmail.com',
            "trade_role": "rolerole1",
            "free_trail": "trailtrail1"
        }
        field_value = self.u1.id
        response = self.client.put(reverse('profile_update', kwargs={'pk': field_value}),data=json.dumps(self.valid_post),content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

