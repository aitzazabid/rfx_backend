# Create your views here.
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile
from core.serializers import ProfileSerializer, UserSerializer
from django.contrib.auth.models import User


class log_in(ObtainAuthToken):

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
        if "email" not in request.data:
            return Response({"success":False, "error": {
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
            profile = self.get_serializer(data=data)
            if profile.is_valid():
                profile.save()
                response = profile.data
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["email"] = user.email
                token, created = Token.objects.get_or_create(user=user)
                response["token"] = token.key
                return Response(response)
            return Response({"success":False, "error": profile._errors})
        return Response({"success":False, "error": user._errors})



