from accounts.models import User

from rest_framework import status, viewsets

from utils.global_utils import validate_fields, create_response
from tasks.authentication import get_tokens_for_user

from accounts.serializer import UserProfileCreateSerializer

import logging

logger = logging.getLogger(__name__)

class SignupWithPassword(viewsets.ViewSet):

    def create(self, request):
        data = request.data

        logger.info("Signup attempt with data: %s", data)

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
                logger.warning("Validation failed: %s", response)
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=response
                )
            
            if User.objects.filter(username=user_name).exists():
                logger.info("Username already exists: %s", user_name)
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="username already exists"
                )
            
            if User.objects.filter(email=email).exists():
                logger.info("Email already exists: %s", email)
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="E-mail already exists"
                )
            
            serialized_user_obj = UserProfileCreateSerializer(data=data)
            if serialized_user_obj.is_valid():
                user = serialized_user_obj.save()
                logger.info("User created successfully: %s", user)
                token = get_tokens_for_user(user) 

                return create_response(
                    message="User created Successfully",
                    status=status.HTTP_201_CREATED, 
                    result=token
                )

            else:
                logger.warning("Serialization errors: %s", serialized_user_obj.errors)
                return create_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serialized_user_obj.errors
                )
            
        except Exception as e:
            logger.error("Exception during signup: %s", e, exc_info=True)
            return create_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception : {e}"
            )
        
class LoginWithPassword(viewsets.ViewSet):
    def create(self, request):
        logger.info("Login attempt with email: %s", request.data.get("email"))

        try:
            email = request.data.get("email")
            password = request.data.get("password")

            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                logger.warning("User not found for email: %s", email)
                return create_response(
                    status=status.HTTP_404_NOT_FOUND,
                    message="User not found"
                )
            
            if user_obj.password != password:
                logger.warning("Invalid password for user: %s", email)
                return create_response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    message="Invalid Password"
                )
            
            token = get_tokens_for_user(user_obj)

            logger.info("User logged in successfully: %s", email)
            
            return create_response(
                status=status.HTTP_200_OK,
                message="User Logged in Successfully",
                result={"access_token":token['access'],"refresh_token":token['refresh']}
            )

        except Exception as e:
                logger.error("Exception during login for email %s: %s", email, e, exc_info=True)
                return create_response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message=f"Exception : {e}"
                )