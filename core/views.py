# Create your views here.
import pdb

import authentication as authentication
from rest_framework import viewsets, status, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile, Category, Subcategory, ChildSubcategory
from core.serializers import ProfileSerializer, \
    UserSerializer, SearchProfileSerializer, \
    ResetPasswordSerializer, CategorySerializer, \
    SubCategorySerializer, CategorySubcategorySerializer, ChildSubCategorySerializer
from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from random import randint
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from rfx_backend.settings import DEFAULT_FROM_EMAIL


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["email"]).first()
        # if user.profile.expires_in > timezone.now() and user.profile.verified == True:
        if user:
            if user.check_password(request.data["password"]):
                token, created = Token.objects.get_or_create(user=user)
                response = ProfileSerializer(user.profile).data
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["email"] = user.email
                response["token"] = token.key
                return Response(response)

        return Response({
            "success": False,
            "message": "user does not exists"
        })


class LogoutView(APIView):

    def put(self, request):
        # simply delete the token to force a login
        dt = request.data
        token = dt.get('token')
        t = Token.objects.filter(key=token).delete()
        return Response({'success': True, "message": "Logout success full"},
                        status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def create(self, request, *args, **kwargs):
        value = randint(100000, 999999)
        # request.data._mutable = True
        if "email" not in request.data:
            return Response({"success": False, "error": {
                "email": [
                    "This field is required"
                ]
            }})
        user_data = request.data
        # request.data._mutable = True
        user_data["username"] = request.data["email"]

        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            user.set_password(request.data["password"])
            user.save()
            data = request.data
            data["user"] = user.id
            data["email_verification_key"] = value
            data["expires_in"] = timezone.now() + timedelta(days=3)
            profile = self.get_serializer(data=data)
            if profile.is_valid():
                profile.save()
                response = profile.data
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["email"] = user.email
                response["user"] = user.first_name
                token, created = Token.objects.get_or_create(user=user)
                response["token"] = token.key
                return Response(response)
            return Response({"success": False, "error": profile._errors})
        return Response({"success": False, "error": user._errors})

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response({"success": False, "error": serializer._errors})

        return Response(serializer.data)


class ProfileSearchListView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SearchProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name']


class ResetPassword(generics.UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_pwd")):
                return Response({"old_pwd": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_pwd"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    @action(detail=False, methods=['get'])
    def all(self, request):
        query_set = Category.objects.all()
        response = CategorySubcategorySerializer(query_set, many=True).data
        return Response(response)


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubCategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]


class ChildSubCategoryViewSet(viewsets.ModelViewSet):
    queryset = ChildSubcategory.objects.all()
    serializer_class = ChildSubCategorySerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]


class GoogleSignViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def create(self, request, *args, **kwargs):
        if "google_id" not in request.data:
            return Response({"success": False, "error": {
                "google_id": [
                    "This field is required"
                ]
            }})
        email = request.data["google_id"]
        password = str(email) + "rfx_password"
        user_data = request.data
        user_data["username"] = request.data["email"]
        user_data["password"] = password
        user = UserProfile.objects.filter(google_id=request.data["google_id"]).first()
        if user:
            user = user.user
            token, created = Token.objects.get_or_create(user=user)
            response = ProfileSerializer(user.profile).data
            response["first_name"] = user.first_name
            response["last_name"] = user.last_name
            response["email"] = user.email
            response["token"] = token.key
            return Response(response)
        else:
            user = UserSerializer(data=user_data)
            if user.is_valid():
                user = user.save()
                user.set_password(password)
                user.save()

                data = request.data
                data["user"] = user.id
                profile = self.get_serializer(data=data)
                if profile.is_valid():
                    profile.save()
                    response = profile.data
                    response["first_name"] = user.first_name
                    response["last_name"] = user.last_name
                    response["email"] = user.email
                    response["user"] = user.first_name
                    token, created = Token.objects.get_or_create(user=user)
                    response["token"] = token.key
                    return Response(response)
                return Response({"success": False, "error": profile._errors})
            return Response({"success": False, "error": user._errors})


class VerifyEmail(viewsets.ModelViewSet):
    # authentication_classes = (TokenAuthentication,)

    def get_user_data(self, request):
        token = request.GET['token']
        user = UserProfile.objects.filter(email_verification_key=token).first()
        if user:
            if user.expires_in > timezone.now():
                user.verified = True
                user.email_verification_key = None
                return Response({
                    "Success": True,
                    "message": "Your account in verify"
                })
        return Response({
            "Success": False,
            "message": "Email verification key is expired"
        })


class ForgotPassword(viewsets.ModelViewSet):

    def get_email(self, request):
        import pdb;
        pdb.set_trace()
        user_data = request.data
        email = user_data["email"]
        token = request.GET['token']
        ctx = {
            'link': 'http://18.118.115.142/forgot-password?token=' + token,
            'email': email
        }

        html_content = render_to_string(template_name='reset_password.html', context=ctx)
        text_content = render_to_string(template_name='reset_password.html', context=ctx)

        try:
            msg = EmailMultiAlternatives('Forgot password', text_content, DEFAULT_FROM_EMAIL, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.mixed_subtype = 'related'
            msg.send()
        except:
            print("error")
