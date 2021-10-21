# Create your views here.
import pdb

from rest_framework import viewsets, status, generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile, Category, Subcategory
from core.serializers import ProfileSerializer,\
    UserSerializer, SearchProfileSerializer,\
    ResetPasswordSerializer, CategorySerializer,\
    SubCategorySerializer, CategorySubcategorySerializer
from django.contrib.auth.models import User
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action



class Login(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        user = User.objects.filter(username=request.data["email"]).first()
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
        return Response({'success': True, "message":"Logout success full"},
                        status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def create(self, request, *args, **kwargs):
        # request.data._mutable = True
        if "email" not in request.data:
            return Response({"success":False, "error": {
                    "email": [
                        "This field is required"
                    ]
                }})
        user_data = request.data
        #request.data._mutable = True
        user_data["username"] = request.data["email"]
        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            user.set_password(request.data["password"])
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

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)

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




