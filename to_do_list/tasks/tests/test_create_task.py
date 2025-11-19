import pytest
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta

from tasks.models import task
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestTaskCreateAPI:

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="john",
            email="john@mail.com",
            password="123"
        )

    @pytest.fixture
    def auth_client(self, client, user):
        client.force_authenticate(user)
        return client

    @pytest.fixture
    def url(self):
        return "/api/tasks/create-task/"


    def test_create_task_successful(self, auth_client, url):
        payload = {
            "title": "My Task",
            "description": "Test description",
            "status": "not_started",
            "due_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        }

        response = auth_client.post(url, payload, format="json")
        body = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert body["message"] == "Post created successfully."
        assert body["result"]["title"] == "My Task"
        assert body["result"]["status"] == "not_started"


    def test_invalid_status(self, auth_client, url):
        payload = {
            "title": "Bad Task",
            "description": "desc",
            "status": "WRONG_STATUS",
            "due_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        }

        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid Status" in response.json()["message"]


    def test_duplicate_title(self, auth_client, user, url):
        task.objects.create(
            title="Duplicate",
            description="old",
            status="not_started",
            due_date=date.today() + timedelta(days=5),
            user=user
        )

        payload = {
            "title": "Duplicate",
            "description": "new",
            "status": "not_started",
            "due_date": (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
        }

        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["message"]


    def test_invalid_due_date(self, auth_client, url):
        yesterday = (date.today()).strftime("%Y-%m-%d")

        payload = {
            "title": "Bad Date",
            "description": "desc",
            "status": "not_started",
            "due_date": yesterday,
        }

        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid Due Date" in response.json()["message"]


    def test_serializer_errors(self, auth_client, url, monkeypatch):

        class MockSerializer:
            def __init__(self, data):
                self.data = data
                self.errors = {"title": ["This field is required."]}

            def is_valid(self):
                return False

        monkeypatch.setattr(
            "tasks.api.tasks_view.TaskCreateSerializer",
            lambda data: MockSerializer(data)
        )

        payload = {
            "title": "",
            "description": "desc",
            "status": "not_started",
            "due_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        }

        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "required" in str(response.json()["message"]).lower()


    def test_internal_server_error(self, auth_client, url, monkeypatch):

        def explode(*args, **kwargs):
            raise Exception("Forced Crash")

        monkeypatch.setattr(
            "tasks.api.tasks_view.TaskCreateSerializer",
            explode
        )

        payload = {
            "title": "Crash Task",
            "description": "desc",
            "status": "not_started",
            "due_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        }

        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Exception error" in response.json()["message"]
