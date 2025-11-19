import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestSignupWithPassword:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def url(self):
        return "/api/accounts/signup/"

    @pytest.mark.parametrize(
        "payload, field",
        [
            ({"email": "test@mail.com", "password": "Pass123!"}, "username"),
            ({"username": "user1", "password": "Pass123!"}, "email"),
            ({"username": "user1", "email": "test@mail.com"}, "password"),
        ],
    )
    def test_missing_fields(self, client, url, payload, field):
        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 400

        normalized_keys = [k.replace("-", "").replace(" ", "").lower() for k in body["message"].keys()]
        assert field.lower() in normalized_keys


    def test_username_exists(self, client, url):
        User.objects.create(username="john", email="john@mail.com", password="123")

        payload = {
            "username": "john",
            "email": "new@mail.com",
            "password": "Pass123!"
        }

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 400
        assert "username already exists" in body["message"]


    def test_email_exists(self, client, url):
        User.objects.create(username="user1", email="used@mail.com", password="123")

        payload = {
            "username": "newuser",
            "email": "used@mail.com",
            "password": "Pass123!"
        }

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 400
        assert "E-mail already exists" in body["message"]


    def test_successful_signup(self, client, url):
        payload = {
            "username": "newuser",
            "email": "valid@mail.com",
            "password": "StrongPass123!"
        }

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 201
        assert body["message"] == "User created Successfully"
        assert "result" in body

        # Correct token field
        assert "access" in body["result"]
        assert body["result"]["access"] != ""


    def test_serializer_errors(self, client, url, monkeypatch):

        class MockSerializer:
            def __init__(self, data):
                self.data = data
                self._errors = {"username": ["Invalid username"]}

            def is_valid(self):
                return False

            @property
            def errors(self):
                return self._errors

        monkeypatch.setattr(
            "accounts.api.login_signup_view.UserProfileCreateSerializer",
            lambda data: MockSerializer(data)
        )

        payload = {
            "username": "badname",
            "email": "valid@mail.com",
            "password": "StrongPass123!"
        }

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 400
        assert "Invalid username" in str(body["message"])


    def test_internal_error(self, client, url, monkeypatch):

        def raise_exception(*args, **kwargs):
            raise Exception("forced error")

        monkeypatch.setattr(
            "accounts.api.login_signup_view.UserProfileCreateSerializer",
            raise_exception
        )

        payload = {
            "username": "newuser",
            "email": "valid@mail.com",
            "password": "StrongPass123!"
        }

        response = client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == 500
        assert "Exception" in body["message"]
