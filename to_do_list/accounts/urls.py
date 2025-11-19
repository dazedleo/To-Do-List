from django.urls import path, include

from accounts.api.login_signup_view import SignupWithPassword, LoginWithPassword

urlpatterns = [
    path("signup/", SignupWithPassword.as_view({"post":"create"}), name="signup_with_password"),
    path("login/", LoginWithPassword.as_view({"post":"create"}), name="login_with_password"),
]