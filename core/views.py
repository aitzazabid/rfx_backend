# Create your views here.
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import UserProfile
from core.serializers import ProfileSerializer, UserSerializer


class log_in(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']
        token, created = Token.objects.get_or_create(user__username=user)
        return Response({
            'is_success': True,
            'token': token.key,
            'user_id': token.user.id,
            'username': token.user.username,
            'email': token.user.email},
            status=status.HTTP_201_CREATED)


class LogoutView(APIView):

    def put(self, request):
        # simply delete the token to force a login
        dt = request.data
        token = dt.get('token')
        t = Token.objects.filter(key=token).delete()
        return Response({'is_success': True},
                        status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()
        if "email" not in request.data:
            return Response({"success":False, "error": {
                    "email": [
                        "This field is required"
                    ]
                }})
        user_data = request.data
        user_data["username"] = request.data["company_name"]
        user = UserSerializer(data=user_data)
        if user.is_valid():
            user = user.save()
            data = request.data
            data["user"] = user.id
            profile = self.get_serializer(data=data)
            if profile.is_valid():
                profile.save()
                response = profile.data
                response["firstname"] = user.first_name
                response["lastname"] = user.last_name
                response["email"] = user.email
                token, created = Token.objects.get_or_create(user=user)
                response["token"] = token.key
                response["company_name"] = user.username
                return Response(response)
            return Response({"success":False, "error": profile._errors})
        return Response({"success":False, "error": user._errors})



