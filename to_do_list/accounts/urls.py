from django.urls import path, include

from accounts.api.login_signup_view import SignupWithPassword, LoginWithPassword
from accounts.api.token import MyTokenObtainPairView

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup/", SignupWithPassword.as_view({"post":"create"}), name="signup_with_password"),
    path("login/", LoginWithPassword.as_view({"post":"create"}), name="login_with_password"),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]