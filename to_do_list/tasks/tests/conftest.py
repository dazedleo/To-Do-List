import pytest
from rest_framework.test import APIClient
from accounts.models import User


@pytest.fixture
def user(db):
    return User.objects.create(
        username="testuser",
        email="test@mail.com",
        password="1234"
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    # If your project uses JWT:
    from accounts.api.login_signup_view import get_tokens_for_user
    token = get_tokens_for_user(user)["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
