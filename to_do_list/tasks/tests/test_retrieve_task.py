import pytest
import uuid
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from tasks.models import task


@pytest.mark.django_db
class TestTaskRetrieveAPI:

    @pytest.fixture
    def url(self):
        return reverse("retrieve_task")

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_success_retrieve(self, auth_client, user, url):
        task_obj = task.objects.create(
            title="Test Task",
            description="Sample task",
            user=user,
        )

        response = auth_client.get(url, {"task_id": task_obj.id})
        data = response.json()

        assert response.status_code == 200
        assert data["message"] == "Task found successfully."
        assert data["result"]["id"] == str(task_obj.id)

    def test_task_not_found(self, auth_client, url):
        invalid_uuid = uuid.uuid4()

        response = auth_client.get(url, {"task_id": invalid_uuid})
        data = response.json()

        assert response.status_code == 404
        assert data["message"] == "Task not found."

    def test_missing_task_id(self, auth_client, url):
        response = auth_client.get(url)
        data = response.json()

        assert response.status_code == 404

    def test_internal_server_error(self, auth_client, url, monkeypatch):

        def mock_get(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(task.objects, "get", mock_get)

        response = auth_client.get(url, {"task_id": uuid.uuid4()})
        data = response.json()

        assert response.status_code == 500
        assert "Exception" in data["message"]
