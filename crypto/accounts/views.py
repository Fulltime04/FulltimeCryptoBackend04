from jwt import ExpiredSignatureError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from .models import OTP, OTPPurpose
from .serializers import RegisterSerializers, VerifyOTPSerializer, LoginSerializer, ForgotPasswordSerializer, VerifyPasswordResetOTPSerializer, VerifyPasswordSerializer, ResendOTPSerializer
from .utils import create_otp, send_otp_email
from rest_framework.permissions import IsAuthenticated


from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = RegisterSerializers(
            data=request.data,
        )

        print("Registered Data: ", request.data)

        if serializer.is_valid():

            user = serializer.save()

            otp = create_otp(
                user=user,
                purpose=OTPPurpose.EMAIL_VERIFICATION,
            )

            print(OTPPurpose.EMAIL_VERIFICATION)

            send_otp_email(user, otp)

            return Response({
                "success": True,
                "message": "Registration successful. Please check your email for the verification code.",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_201_CREATED)


        return Response({
            "success": False,
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)




class VerifyOTPView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        print("OTP Verification: ", request.data)

        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        otp = OTP.objects.filter(
            user=user,
            code=code,
            purpose=OTPPurpose.EMAIL_VERIFICATION,
            is_used=False,
        ).first()

        if not otp:
            return Response(
                {"message": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp.is_expired():
            return Response(
                {"message": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp.is_used = True
        otp.save()

        user.email_verified = True
        user.save()

        return Response(
            {
                "success": True,
                "message": "Email verified successfully.",
            }
        )





class LoginView(APIView):

    permission_classes = []

    def post(self, request):

        print("Logins Data: ", request.data)

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        print("USER: ", user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },

                "tokens": {
                    "access": str(refresh.access_token),

                    "refresh": str(refresh),
                }

            }
        },
            status=status.HTTP_200_OK,
        )



class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response(
            {
                "message": "You are authenticated.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "email_verified": user.email_verified,
                }
            },
            status=status.HTTP_200_OK
        )



class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):

        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "success": True,
                "message": "Password reset OTP has been sent to your email."
            },
            status=status.HTTP_200_OK
        )



class VerifyPasswordResetView(APIView):
    permission_classes = []

    def post(self, request):

        serializer = VerifyPasswordResetOTPSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "success": True,
                "message": "OTP verified successfully.",
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):

        serializer = VerifyPasswordSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)


        user = serializer.validated_data["user"]
        otp = serializer.validated_data["otp"]

        user.set_password(
            serializer.validated_data["password"]
        )

        user.save()

        otp.is_used = True

        otp.save(
            update_fields=["is_used"]
        )

        return Response(
            {
                    "success": True,
                    "message": "Password reset successfully. You can now log in."
                },
                status=status.HTTP_200_OK
        )



class ResendOTPView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = ResendOTPSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        purpose = serializer.validated_data["purpose"]

        otp = create_otp(
            user=user,
            purpose=purpose
        )

        send_otp_email(
            user=user,
            otp=otp
        )

        return Response(
            {
                "success": True,
                "message": "A new verification code has been sent."
            },
            status=status.HTTP_200_OK
        )




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                "success": False,
                "details": "Refresh Token is required."
                },
             status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)

            token.blacklist()

            return Response(
                {
                    "success": True,
                    "details": "Logout successful."
                },
                status=status.HTTP_200_OK
            )

        except Exception:

            return Response(
                {
                "success": False,
                "details": "Logout failed."
            },
                status=status.HTTP_400_BAD_REQUEST
            )



# Create your views here.


