from accounts.models import User

from rest_framework import status, viewsets

from utils.global_utils import validate_fields, create_response
from tasks.authentication import get_tokens_for_user, get_access_token_from_refresh

from accounts.serializer import UserProfileCreateSerializer

class SignupWithPassword(viewsets.ViewSet):

    def create(self, request):
        data = request.data

        try:

            user_name = data.get('username')
            email = data.get('email')
            password = data.get('password')

            validation_fields = {
                "User Name": {"value":user_name, "checks":['empty','username']},
                "E-mail":{"value":email, "checks":['empty','email']},
                "Password":{"value":password, "checks":['empty','password']}
            }

            response = validate_fields(validation_fields)

            if response:
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=response
                )
            
            if User.objects.filter(username=user_name).exists():
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="username already exists"
                )
            
            if User.objects.filter(email=email).exists():
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="E-mail already exists"
                )
            
            serialized_user_obj = UserProfileCreateSerializer(data=data)
            if serialized_user_obj.is_valid():
                user = serialized_user_obj.save()
                token = get_tokens_for_user(user) 

                return create_response(
                    message="User created Successfully",
                    status=status.HTTP_201_CREATED, 
                    result=token
                )

            else:
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serialized_user_obj.errors
                )
            
        except Exception as e:
            return create_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception : {e}"
            )
        
class LoginWithPassword(viewsets.ViewSet):
    def create(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            refresh = request.data.get("refresh")

            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return create_response(
                    status=status.HTTP_404_NOT_FOUND,
                    message="User not found"
                )
            
            if user_obj.password != password:
                return create_response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    message="Invalid Password"
                )
            
            token = get_access_token_from_refresh(refresh)

            if not token['refresh_valid']:
                token = get_tokens_for_user(user_obj)
            
            return create_response(
                status=status.HTTP_200_OK,
                message="User Logged in Successfully",
                result={"access_token":token['access'],"refresh_token":token['refresh']}
            )

        except Exception as e:
                import traceback
                traceback.print_exc()
                return create_response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Exception : {e}"
                )