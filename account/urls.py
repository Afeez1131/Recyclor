from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
)
from account import views

# app_name = "account"

urlpatterns = [
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.RegisterUserView.as_view(), name="register"),
    path(
        "password-reset",
        PasswordResetView.as_view(template_name="account/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done",
        PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>",
        PasswordResetConfirmView.as_view(
            template_name="account/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete",
        PasswordResetCompleteView.as_view(
            template_name="account/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
