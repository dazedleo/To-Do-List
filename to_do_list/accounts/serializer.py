from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import User


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