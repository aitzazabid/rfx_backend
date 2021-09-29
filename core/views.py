from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
# from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
# from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import UserProfile
from core.serializers import ProfileSerializer


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['username']
        user = User.objects.get(username=user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'is_success': True,
            'token': token.key,
            'user_id': user.id,
            'name': user.username,
            'email': user.email},
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
    permission_classes = [IsAuthenticated]
