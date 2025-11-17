from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import status

from utils.global_utils import create_response

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_access_token_from_refresh(refresh_token_str):
    try:
        refresh = RefreshToken(refresh_token_str)
        
        # Generate a new access token
        new_access_token = str(refresh.access_token)
        
        return {
            'access': new_access_token,
            'refresh_valid': True
        }
    except TokenError as e:
        return {
            'error': 'Invalid or expired refresh token',
            'refresh_valid': False
        }
