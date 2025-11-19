import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User

@pytest.mark.django_db
class TestLoginWithPassword:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def url(self):
        return "/api/accounts/login/"


    @pytest.mark.parametrize(
        "payload, missing_field",
        [
            ({"password": "pass123"}, "email"),
            ({"email": "user@mail.com"}, "password"),
        ]
    )
    def test_missing_fields(self, client, url, payload, missing_field):

        response = client.post(url, payload, format="json")
        body = response.json()

        if missing_field == "email":
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in body["message"]

        if missing_field == "password":
            User.objects.create(email="user@mail.com", username="test", password="correctpass")

            response = client.post(url, payload, format="json")
            body = response.json()

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid Password" in body["message"]


    def test_user_not_found(self, client, url):
        payload = {"email": "nouser@mail.com", "password": "abc123"}

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert body["message"] == "User not found"


    def test_invalid_password(self, client, url):
        User.objects.create(email="test@mail.com", username="test", password="correctpass")

        payload = {"email": "test@mail.com", "password": "wrongpass"}

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert body["message"] == "Invalid Password"


    def test_successful_login(self, client, url):
        user = User.objects.create(email="test@mail.com", username="test", password="mypassword")

        payload = {"email": "test@mail.com", "password": "mypassword"}

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert body["message"] == "User Logged in Successfully"
        assert "result" in body
        assert "access_token" in body["result"]
        assert "refresh_token" in body["result"]
        assert body["result"]["access_token"] != ""


    def test_internal_exception(self, client, url, monkeypatch):

        def raise_error(*args, **kwargs):
            raise Exception("forced error")

        monkeypatch.setattr(
            "accounts.api.login_signup_view.User.objects.filter",
            raise_error
        )

        payload = {"email": "a@mail.com", "password": "123"}

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Exception" in body["message"]
