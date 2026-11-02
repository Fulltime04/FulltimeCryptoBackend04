from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .managers import UserManager

class User(AbstractUser):

    username = models.CharField(
        max_length=30,
    )

    email = models.EmailField(unique=True)

    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    phone_number = models.CharField(max_length=11, unique=True, null=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    objects = UserManager()

    def __str__(self):
        return self.email



class OTPPurpose(models.TextChoices):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION", "email_verification"
    PASSWORD_RESET = "PASSWORD_RESET", "password_reset"



class OTP(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps"
    )


    code = models.CharField(
        max_length=6,
    )

    purpose = models.CharField(
        max_length=30,
        choices=OTPPurpose.choices,
    )

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    expired_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expired_at

    def __str__(self):
        return f"{self.user.email} - {self.code}"






# Create your models here.
# Create your models here.
# Create your models here.
# Create your models here.
# Create your models here.
