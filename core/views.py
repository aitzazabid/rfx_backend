# Create your views here.

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
from rest_fuzzysearch import search, sort
from core.utils import send_verification_email, allow_user_login
from django.shortcuts import redirect

REST_ERROR_CODE = "rest_error"
VERIFICATION_REQUIRED = 1


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["email"]).first()
        allow_login = allow_user_login(user)
        if allow_login:
            if user.check_password(request.data["password"]):
                token, created = Token.objects.get_or_create(user=user)
                response = ProfileSerializer(user.profile).data
                user.profile.check_login_attempt += 1
                user.profile.save()
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["email"] = user.email
                response["token"] = token.key
                response["success"] = True
                response["login_attempt"] = user.profile.check_login_attempt

                return Response(response)

            else:
                return Response({
                    "success": False,
                    "message": "user does not exists"
                })
        else:
            return Response({
                "success": False,
                "message": "user does not exists",
                REST_ERROR_CODE: VERIFICATION_REQUIRED
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

    def create(self, request, *args, **kwargs):
        if "email" not in request.data:
            return Response({"success": False, "error": {
                "email": [
                    "This field is required"
                ]
            }})
        user_data = request.data
        user_data["username"] = request.data["email"]

        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            user.set_password(request.data["password"])
            user.save()
            data = request.data
            data["user"] = user.id
            data["expires_in"] = timezone.now() + timedelta(days=3)
            data["first_name"] = user.first_name
            data["last_name"] = user.last_name
            data["check_login_attempt"] = 0
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
                response["login_attempt"] = 0

                return Response(response)
            return Response({"success": False, "error": profile._errors})
        return Response({"success": False, "error": user._errors})

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        user_mobile_number = request.data.get("user_mobile_number", None)
        data = request.data
        if not user_mobile_number or len(user_mobile_number) != 0:
            del data["user_mobile_number"]
        user = request.user
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response({"success": False, "error": serializer._errors})

        return Response(serializer.data)


class UpdateProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not allow_user_login(request.user):
            return Response({
                "success": False,
                "message": "user does not exists",
                REST_ERROR_CODE: VERIFICATION_REQUIRED
            })
        partial = True
        instance = self.get_object()
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        user = request.user
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
        else:
            return Response({"success": False, "error": serializer._errors})

        return Response(serializer.data)


class SendVerificationEmail(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request):
        email = request.data.get("email", None)
        user = User.objects.filter(email=email).first()

        to_email = user.email
        name = user.first_name
        value = randint(100000, 999999)
        user.profile.email_verification_key=value
        user.profile.save()
        print("value", value)
        send_verification_email(to_email, value, name)
        return Response({
            "success": True,
            "message": "verification email sent"
        })


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
                user.save()
                return redirect("http://rfxmedemo.com")
        return redirect("http://rfxmedemo.com/error-message")


class ForgotPassword(viewsets.ModelViewSet):

    def get_email(self, request):
        if request.data.get("email", None):
            user_data = request.data
            email = user_data["email"]
            value = randint(100000, 999999)
            ctx = {
                'link': 'http://rfxmedemo.com/forgot-password/' + str(value),
                'email': email
            }
            user = UserProfile.objects.filter(user__email=email).first()
            if not user:
                return Response({"success": False, "error": "User does not exist"})
            else:
                user.forgot_password = value
                user.save()
                html_content = render_to_string(template_name='forgot_password.html', context=ctx)
                text_content = render_to_string(template_name='forgot_password.html', context=ctx)
                try:
                    msg = EmailMultiAlternatives('Forgot password', text_content, DEFAULT_FROM_EMAIL, [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.mixed_subtype = 'related'
                    msg.send()
                    return Response({'value': value})
                except Exception as e:
                    print("error", e)
        elif request.data.get("token", None):
            user_data = request.data
            token1 = user_data["token"]
            user = UserProfile.objects.filter(forgot_password=token1).first()
            if user:
                user.user.set_password(request.data["new_password"])
                user.user.save()
                return Response('success: Okay')
            else:
                return Response({"success": False, "error": "User does not exist"})
        else:
            return Response({"success": False, "error": "User does not exist"})


class FuzzySearchView(sort.SortedModelMixin, search.SearchableModelMixin, viewsets.ReadOnlyModelViewSet):
    lookup_fields = ('company_name', 'company_brand', 'category')
    lookup_value_regex = '[^/]+'
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    filter_backends = (search.RankedFuzzySearchFilter, sort.OrderingFilter)
    search_fields = ('company_name', 'company_brand', 'category')
    ordering = ('-rank',)

    min_rank = 0.1
