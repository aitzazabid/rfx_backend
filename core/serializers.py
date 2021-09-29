from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
