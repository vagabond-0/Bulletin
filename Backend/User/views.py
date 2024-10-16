from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import AlumniSerializer
from .models import Alumni

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            alumni = Alumni.objects.get(email=email)
            user = authenticate(username=alumni.user.username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                serializer = AlumniSerializer(alumni)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': serializer.data
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Alumni.DoesNotExist:
            return Response({'error': 'Alumni not found'}, status=status.HTTP_404_NOT_FOUND)
