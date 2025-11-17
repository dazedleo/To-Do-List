from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializer import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer