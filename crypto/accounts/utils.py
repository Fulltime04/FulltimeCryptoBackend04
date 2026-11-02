import random
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import OTP

def generate_otp():
    """
    Generate a random OTP
    :return:
    """

    return random.randint(100000, 999999)

def create_otp(user, purpose):
    """
     CREATE OTP FOR A USER
    :param user:
    :param purpose:
    :return:
    """


    OTP.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False
    ).update(is_used=True)


    otp = OTP.objects.create(
        user=user,
        purpose=purpose,
        code=generate_otp(),
        expired_at=timezone.now() + timedelta(minutes=10),
    )

    return otp



def send_otp_email(user, otp):
    if otp.purpose == "EMAIL_VERIFICATION":

        subject = "EMAIL VERIFICATION"

        message = f"""
Hello {user.first_name},

Welcome! to Rockers Crypto Tracker.

Your verification code is:

{otp.code}

This code expires in 10 minutes.

If you didn't create this account, please ignore this email.

Regards,

Rockers Crypto Tracker Team
"""

    elif otp.purpose == "PASSWORD_RESET":

        subject = "PASSWORD RESET"

        message = f"""
Hello {user.first_name},

We received a request to reset the password for your account.

Your password reset code is:

{otp.code}

This code expires in 10 minutes.

If you did not request a password reset, please ignore this email.

Regards,

Rockers Crypto Tracker Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

