from django.urls import path
from . import views
from landing.views import home

app_name = "base"

urlpatterns = [
    path("", home, name="home"),  # homepage

    # Signup
    path("signup/", views.signup, name="signup"),

    # Login
    path("login/", views.login_view, name="login"),

    # Forgot Password
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("forgot-password/reset/", views.forgot_password_reset, name="forgot_password_reset"),
      path("verify-otp/", views.verify_otp, name="verify_otp"),

    # Login Options
    path("login/options/", views.login_options, name="login_options"),
]