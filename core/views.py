# Create your views here.
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination

from rest_framework import viewsets, status, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile, Category, Subcategory, ChildSubcategory, Publication, FollowSupplier, AddProducts, \
    MultipleImages, SocialLinks, AddServices
from core.serializers import ProfileSerializer, \
    UserSerializer, SearchProfileSerializer, \
    ResetPasswordSerializer, CategorySerializer, \
    SubCategorySerializer, CategorySubcategorySerializer, ChildSubCategorySerializer, PublicationSerializer, \
    SaveSupplierSerializer, ProductSerializer, MultiImageSerializer, SocialLInksSerializer, AddServicesSerializer
from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from random import randint
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rfx_backend.settings import DEFAULT_FROM_EMAIL
from rest_fuzzysearch import search, sort
from core.utils import send_verification_email, allow_user_login
from django.shortcuts import redirect
from core import constants

REST_ERROR_CODE = "rest_error"
VERIFICATION_REQUIRED = 1


class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["email"]).first()
        if user:
            allow_login = allow_user_login(user)
            if allow_login:
                if user.check_password(request.data["password"]):
                    token, created = Token.objects.get_or_create(user=user)
                    response = ProfileSerializer(user.profile, context={'request': request}).data
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
                        "message": "The password that you've entered is incorrect"
                    })
            return Response({
                "success": False,
                "message": "user does not exists",
                REST_ERROR_CODE: VERIFICATION_REQUIRED
            })
        else:
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
                response["user"] = user.id
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

    def create(self, request):
        email = request.data.get("email", None)
        user = User.objects.filter(email=email).first()

        if user:
            to_email = user.email
            name = user.first_name
            value = randint(100000, 999999)
            user.profile.email_verification_key = value
            user.profile.save()
            print("value", value)
            send_verification_email(to_email, value, name)
            return Response({
                "success": True,
                "message": "verification email sent"
            })
        else:
            return Response({
                "success": False,
                "message": "user does not exists",
                REST_ERROR_CODE: VERIFICATION_REQUIRED
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
            response = ProfileSerializer(user.profile, context={'request': request}).data
            user.profile.expires_in = timezone.now() + timedelta(days=3)
            user.profile.check_login_attempt += 1
            user.profile.save()
            response["first_name"] = user.first_name
            response["last_name"] = user.last_name
            response["email"] = user.email
            response["token"] = token.key
            response["login_attempt"] = user.profile.check_login_attempt
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
                    user.profile.check_login_attempt = 0
                    user.profile.save()
                    response["first_name"] = user.first_name
                    response["last_name"] = user.last_name
                    response["email"] = user.email
                    response["user"] = user.first_name
                    token, created = Token.objects.get_or_create(user=user)
                    response["token"] = token.key
                    response["login_attempt"] = user.profile.check_login_attempt
                    return Response(response)
                return Response({"success": False, "error": profile._errors})
            return Response({"success": False, "error": user._errors})


class VerifyEmail(viewsets.ModelViewSet):

    def get_user_data(self, request):
        token = request.GET['token']
        user = UserProfile.objects.filter(email_verification_key=token).first()
        if user:
            if user.expires_in > timezone.now():
                user.verified = True
                user.email_verification_key = None
                user.save()
                return redirect(constants.login)
        return redirect(constants.error_message)


class ForgotPassword(viewsets.ModelViewSet):

    def get_email(self, request):
        if request.data.get("email", None):
            user_data = request.data
            email = user_data["email"]
            value = randint(100000, 999999)
            ctx = {
                'link': constants.forgot_password + str(value),
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

    def get_queryset(self):
        data = self.request.GET
        user = super(FuzzySearchView, self).get_queryset()
        if data.get('location'):
            user = user.filter(location__in=data.get('location').split(","))
        if data.get('company_type'):
            user = user.filter(company_type__in=data['company_type'].split(","))
        if data.get('no_employee_from') and data.get('no_employee_to'):
            user = user.filter(total_employees__gte=data['no_employee_from'],
                               total_employees__lte=data['no_employee_to'])
        elif data.get('no_employee_from'):
            user = user.filter(total_employees__gte=data['no_employee_from'])
        elif data.get('no_employee_to'):
            user = user.filter(total_employees__lte=data['no_employee_to'])

        if data.get('revenue_from') and data.get('revenue_to'):
            user = user.filter(annual_revenue__gte=data['revenue_from'], annual_revenue__lte=data['revenue_to'])
        elif data.get('revenue_from'):
            user = user.filter(annual_revenue__gte=data['revenue_from'])
        elif data.get('revenue_to'):
            user = user.filter(annual_revenue__lte=data['revenue_to'])
        if data.get('field_of_work'):
            user = user.filter(field_of_work__in=data.get('field_of_work').split(","))
        self.get_serializer(context={'request': user})
        return user


class PublicationView(viewsets.ModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        request.data._mutable = True
        request.data['user'] = user.id
        request.data._mutable = False
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer._errors)

    def list(self, request, *args, **kwargs):
        user = request.user
        user1 = self.queryset.filter(user=user.id)
        return Response(self.get_serializer(user1, many=True).data)


class SaveSupplierView(viewsets.ModelViewSet):
    queryset = FollowSupplier.objects.all()
    serializer_class = SaveSupplierSerializer

    def create(self, request, *args, **kwargs):
        check_save_supplier_user = UserProfile.objects.filter(user_id=request.data['id'])
        if check_save_supplier_user:
            following, created = FollowSupplier.objects.get_or_create(user_id=request.user.id,
                                                                      following_user_id=request.data['id'])
            if created:
                return Response({
                    "success": True,
                    "message": "supplier saved"
                })
            elif following:
                FollowSupplier.objects.filter(user_id=request.user.id,
                                              following_user=request.data['id']).delete()
            return Response({
                "success": True,
                "message": "supplier remove from the save list"
            })
        else:
            return Response({
                "success": False,
                "message": "save supplier does not exist"
            })

    def list(self, request, *args, **kwargs):
        user = request.user
        following = FollowSupplier.objects.filter(user=user).values_list("following_user", flat=True).distinct()
        response = dict()
        response["success"] = True
        response["data"] = []
        if following:
            following = UserProfile.objects.filter(user__id__in=list(following))
            serializer = ProfileSerializer(following, many=True, context={'request': request})

            response["data"] = serializer.data
            return Response(response)
        return Response(response)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class AddProductView(viewsets.ModelViewSet, LimitOffsetPagination):
    queryset = AddProducts.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            return AddProducts.objects.filter(user_id=self.request.user.id)
        return AddProducts.objects.all()

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            images = dict((request.data).lists())['image']
            image = []
            if len(images) <= 4:
                serializer.save()
                for img_name in images:
                    modified_data = {"product": serializer.data['id'], "image": img_name}
                    file_serializer = MultiImageSerializer(data=modified_data)
                    if file_serializer.is_valid():
                        file_serializer.save()
                        image.append(file_serializer.data)
            else:
                return Response({
                    "success": False,
                    "message": "user can upload maximum 4 files",
                })
            data = dict(serializer.data)
            data['image'] = image
            return Response(data)
        return Response(serializer._errors)

    def list(self, request, *args, **kwargs):
        id = kwargs["pk"]
        user = AddProducts.objects.filter(user=id)
        if user:
            return Response(self.get_serializer(user, many=True).data)
        else:
            return Response({
                "success": False,
                "message": "user has no products",
            })


class GetSpecificProd(viewsets.ModelViewSet):
    queryset = AddProducts.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        data = self.request.GET
        prod_id = data.get('id')
        if prod_id:
            get_data = self.queryset.filter(id=prod_id)
            return Response(self.get_serializer(get_data, many=True).data)
        else:
            return Response({
                "success": False,
                "message": "product id not found",
            })


class AddSocialLinksView(viewsets.ModelViewSet):
    queryset = SocialLinks.objects.all()
    serializer_class = SocialLInksSerializer

    def create(self, request, *args, **kwargs):
        id_1 = request.user.id
        user1 = UserProfile.objects.filter(user=id_1)
        if user1:
            user2 = SocialLinks.objects.filter(user=id_1)
            if user2:
                return Response({
                    "success": False,
                    "message": "user already added links",
                })
            else:
                request.data['user'] = request.user.id
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
        else:
            return Response({
                "success": False,
                "message": "user does not exist",
            })

    def list(self, request, *args, **kwargs):
        id_1 = kwargs["pk"]
        user = SocialLinks.objects.filter(user=id_1)
        if user:
            return Response(self.get_serializer(user, many=True).data)
        else:
            return Response({
                "success": False,
                "message": "user not found",
            })

    def update(self, request, *args, **kwargs):
        user_id1 = request.user.id
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            user2 = SocialLinks.objects.filter(user=user_id1)
            if user2:
                partial = True
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({
                    "success": False,
                    "message": "User does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "User does not exist"
            })


class AddServciesView(viewsets.ModelViewSet):
    queryset = AddServices.objects.all()
    serializer_class = AddServicesSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.user.id
        isUser = UserProfile.objects.filter(user=user_id)
        if isUser:
            isUserAlready = AddServices.objects.filter(user=user_id)
            if isUserAlready:
                return Response({
                    "success": False,
                    "message": "user already added services",
                })
            else:
                request.data['user'] = request.user.id
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response({
                        "success": False,
                        "message": "failed",
                    })
        else:
            return Response({
                "success": False,
                "message": "user does not exist",
            })

    def update(self, request, *args, **kwargs):
        user_id1 = request.user.id
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            user2 = AddServices.objects.filter(user=user_id1)
            if user2:
                partial = True
                instance = self.get_object()
                data1 = AddServices.objects.get(id=instance.id)
                request.data['list_skills'] += "," + data1.list_skills
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                if serializer.is_valid():
                    serializer.save()
                    self.perform_update(serializer)
                    return Response(serializer.data)
                else:
                    return Response(serializer._errors)
            else:
                return Response({
                    "success": False,
                    "message": "User does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "User does not exist"
            })

    def destroy(self, request, *args, **kwargs):
        user_id1 = request.user.id
        user_check = UserProfile.objects.filter(user_id=user_id1)
        if user_check:
            user2 = AddServices.objects.filter(user=user_id1)
            if user2:
                data1 = AddServices.objects.get(id=kwargs["pk"],
                                                service_name=request.data["service_name"])
                ex_list = data1.list_skills
                re_list = request.data["list_skills"]
                listt = re_list.split(",")
                for skill in listt:
                    dd = str(skill) + ","
                    ex_list = ex_list.replace(dd, "")

                data1.list_skills = ex_list
                data1.save()
                return Response({
                    "success": True,
                    "message": "Given data deleted"
                })
            else:
                return Response({
                    "success": False,
                    "message": "User does not exist"
                })
        else:
            return Response({
                "success": False,
                "message": "User does not exist"
            })

    def list(self, request, *args, **kwargs):
        id = kwargs["pk"]
        user = AddServices.objects.filter(user=id)
        if user:
            return Response(self.get_serializer(user, many=True).data)
        else:
            return Response({
                "success": False,
                "message": "user has no products",
            })
