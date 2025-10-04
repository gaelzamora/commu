from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer, RegisterStartSerializer, RegisterCompleteSerializer
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .throttles import RegisterStartThrottle
import re
from django.conf import settings
from .utils_tokens import make_registration_token, validate_registration_token
from django.core.mail import send_mail
import os

# Create your views here.

User = get_user_model()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MAGIC_LINK_BASE = getattr(settings, "MAGIC_LINK_BASE", "http://localhost:8000/v1/api/auth/register/verify/")
                                                            
class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token required"}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({"detail": "invalid token"}, status=400)
        return Response(status=205)
    
class RegisterStartView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterStartThrottle]
    serializer_class = RegisterStartSerializer

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].strip().lower()

        if not EMAIL_RE.match(email):
            return Response({"detail": "Invalid email"}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"detail": "email already in use"}, status=400)
        
        token = make_registration_token(email, ttl_minutes=15)
        link = f"{MAGIC_LINK_BASE}?token={token}"

        send_mail(
            subject="Confirm your mail",
            message=f"Hello, confirm your email entering to: {link}\nThe link expires in 15 minutes.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
            recipient_list=[email],
            fail_silently=False,
        )   
        return Response({"detail": "verification sent"})
    
class RegisterVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        raw = request.query_params.get("token")
        if not raw:
            return Response({"detail": "token required"}, status=400)
        try:
            at = AccessToken(raw)
            email = validate_registration_token(at)
        except Exception:
            return Response({"detail": "invalid or expired token"}, status=400)
        
        return Response({"registration_token": str(at), "email": email})
    
class RegisterCompleteView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterCompleteSerializer

    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        token = ser.validated_data["registration_token"]
        username = ser.validated_data["username"]
        first_name = ser.validated_data.get("first_name", "")
        last_name  = ser.validated_data.get("last_name", "")
        password   = ser.validated_data["password"]

        try:
            at = AccessToken(token)
            email = validate_registration_token(at)
        except Exception:
            return Response({"detail": "invalid or expired token"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "email already in use"}, status=400)

        user = User.objects.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})

class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]