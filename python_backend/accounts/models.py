from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin
)
import uuid

RESERVED_USERNAMES = {"admin", "root", "support"}

class UserManager(models.Manager):
    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        """Create and return a regular user with the provided details."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, first_name, last_name, branch=None, password=password, **extra_fields)

    def normalize_email(self, email):
        """Normalize the email address by lowercasing the domain part of it."""
        return email.lower()

    def get_by_natural_key(self, email):
        """Return the user with the given email."""
        return self.get(email=email)


    """User in the system."""
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=22, unique=True)
    bio = models.CharField(max_length=160, default="No bio yet")
    avatar_key = models.CharField(max_length=512, blank=True)
    reputation = models.IntegerField(default=0) 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(max_length=10, blank=True)
    mfa_totp_secret_enc = models.BinaryField(null=True)
    mfa_last_verified_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return self.email