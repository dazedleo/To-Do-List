from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email','password']
        
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['user_id'] = str(user.id)
        token['username'] = user.username
        token['email'] = user.email

        return token