from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    LogoutView,
    ProfileView,
    ForgotPasswordView,
    VerifyPasswordResetView,
    ResetPasswordView,
    ResendOTPView
)
from django.urls import path

urlpatterns = [

    path("register/", RegisterView.as_view(), name="register"),

    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    path("login/", LoginView.as_view(), name="login"),

    path("profile/", ProfileView.as_view(), name="profile"),
    
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),

    path("verify-reset-otp/", VerifyPasswordResetView.as_view(), name="verify_reset_otp"),

    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),

    path("logout/", LogoutView.as_view(), name="logout_view")

]

