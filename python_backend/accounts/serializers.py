from rest_framework import serializers
from .models import User
from .utils_tokens import make_registration_token, validate_registration_token
from django.conf import settings

MAGIC_LINK_BASE = getattr(settings, "MAGIC_LINK_BASE", "https://mi-backend.com/api/auth/register/verify")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "reputation")
        read_only_fields = ("id", "reputation")

class RegisterStartSerializer(serializers.Serializer):
    email = serializers.EmailField()

class RegisterCompleteSerializer(serializers.ModelSerializer):
    registration_token = serializers.CharField()
    username = serializers.CharField(min_length=3, max_length=22)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, v):
        v = v.strip()
        if " " in v:
            raise serializers.ValidationError("username cannot contain spaces")
        if User.objects.filter(username=v).exists():
            raise serializers.ValidationError("username already taken")
        return v
