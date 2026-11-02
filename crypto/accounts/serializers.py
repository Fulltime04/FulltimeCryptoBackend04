from django.contrib.auth import get_user_model
from rest_framework import serializers
from .utils import create_otp, send_otp_email
from .models import OTPPurpose, OTP

User = get_user_model()


class RegisterSerializers(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )


    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )


    class Meta:

        model = User

        fields = (
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
            "confirm_password",
        )


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "details": "An account with this Email already exists."
            })

        return value



    def validate(self, attr):

        if attr['password'] != attr['confirm_password']:
            raise serializers.ValidationError(
                {"details": "Passwords doesn't match."}
            )

        return attr



    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class VerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(
            email=email
        ).first()

        if not user:
            raise serializers.ValidationError({
                "details": "Invalid Email or Password."
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "details": "Invalid Email or Password."
            })

        if not user.email_verified:
            raise serializers.ValidationError({
                "details": "Please verify your email before logging in."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "details": "This account is inactive."
            })

        attrs["user"] = user

        return attrs



class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "details": "No account was found with this email"
            })

        otp = create_otp(
            user=user,
            purpose=OTPPurpose.PASSWORD_RESET
        )

        send_otp_email(
            user=user,
            otp=otp,
        )

        attrs["user"] = user

        return attrs



class VerifyPasswordResetOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(max_length=6,min_length=6)

    def validate(self, attrs):

        email = attrs["email"]

        otp_code = attrs["otp"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "detail": "Invalid Email or OTP"
            })

        try:

            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                purpose=OTPPurpose.PASSWORD_RESET,
                is_used=False,
            ).latest("created_at")

        except OTP.DoesNotExist:
            raise serializers.ValidationError({
                "details": "Invalid or Already Used OTP"
            })


        if otp.is_expired():

            raise serializers.ValidationError({
                "details": "OTP expired, Please request for a new one"
            })


        attrs["user"] = user

        attrs["otp"] = otp

        return attrs




class VerifyPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        email = attrs["email"]
        otp_code = attrs["otp"]
        password = attrs["password"]
        confirm_password = attrs["confirm_password"]

        if password != confirm_password:

            raise serializers.ValidationError({
                "details": "Passwords don't match."
            })

        try:

            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "details": "Invalid Email or OTP"
            })

        try:

            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                purpose=OTPPurpose.PASSWORD_RESET,
                is_used=False,
            ).latest("created_at")

        except OTP.DoesNotExist:

            raise serializers.ValidationError({
                "details": "Invalid or Already Used OTP"
            })

        if otp.is_expired():

            raise serializers.ValidationError({
                "details": "ooops OTP expired, Please request for a new one"
            })

        attrs["user"] = user
        attrs["otp"] = otp

        return attrs



class ResendOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.choices
    )

    def validate(self, attrs):

        email = attrs["email"]
        purpose = attrs["purpose"]

        try:
            user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:
            raise serializers.ValidationError({
                "detail": "No account was found with this email."
            })

        # Don't resend registration OTP
        # if the email is already verified.

        if (
            purpose == OTPPurpose.EMAIL_VERIFICATION
            and user.email_verified
        ):
            raise serializers.ValidationError({
                "detail": "This email is already verified."
            })

        attrs["user"] = user

        return attrs









