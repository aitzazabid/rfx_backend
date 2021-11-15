from rest_framework import serializers
from core.models import UserProfile, Category, Subcategory, ChildSubcategory, Publication, FollowSupplier
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField(read_only=True)

    def get_is_saved(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            if FollowSupplier.objects.filter(user_id=user.id, following_user_id=obj.id).exists():
                return True
            return False

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = UserProfile
        fields = "__all__"
        extra_kwargs = {'email_verification_key': {'write_only': True}}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('title', 'dob', 'address', 'country', 'city', 'zip')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}


class SearchProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    class Meta:
        model = UserProfile
        fields = "__all__"


class ResetPasswordSerializer(serializers.Serializer):
    model = User
    old_pwd = serializers.CharField(required=True)
    new_pwd = serializers.CharField(required=True)


class ChildSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildSubcategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SubCategorySerializer(serializers.ModelSerializer):
    child_categories = ChildSubCategorySerializer(source='child_category', many=True, read_only=True)

    class Meta:
        model = Subcategory
        fields = "__all__"


class CategorySubcategorySerializer(serializers.ModelSerializer):
    sub_categories = SubCategorySerializer(source='category', many=True, read_only=True)

    class Meta:
        model = Category
        fields = "__all__"


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"


class SaveSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowSupplier
        fields = "__all__"
