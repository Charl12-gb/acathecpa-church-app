from django.urls import path

from .views_auth import (
    ForgotPasswordView,
    LoginView,
    MeView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    ValidateUsernameView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="auth-register"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("login/flexible", LoginView.as_view(), name="auth-login-flexible"),
    path("token/refresh", RefreshTokenView.as_view(), name="auth-token-refresh"),
    path("forgot-password", ForgotPasswordView.as_view(), name="auth-forgot-password"),
    path("reset-password", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("users/me", MeView.as_view(), name="auth-me"),
    path("validate-username/<str:username>", ValidateUsernameView.as_view(), name="auth-validate-username"),
]
