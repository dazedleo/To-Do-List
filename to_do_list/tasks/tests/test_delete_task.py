import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tasks.models import task
from datetime import date, timedelta

@pytest.fixture
def url():
    return reverse("destroy_task")

@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
class TestTaskDeleteAPI:

    def test_success_delete(self, auth_client, user, url):
        t = task.objects.create(
            title="TaskToDelete",
            due_date=date.today() + timedelta(days=3),
            status="not_started",
            user=user
        )

        response = auth_client.delete(f"{url}?task_id={t.id}")

        assert response.status_code == 200
        assert response.json()["message"] == "Task deleted successfully."

        # Ensure is_deleted is True in the DB
        t.refresh_from_db()
        assert t.is_deleted is True

    def test_task_not_found(self, auth_client, url):
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = auth_client.delete(f"{url}?task_id={non_existent_id}")

        assert response.status_code == 404
        assert response.json()["message"] == "Task not found."

    def test_internal_server_error(self, auth_client, user, url, monkeypatch):
        t = task.objects.create(
            title="TaskCrash",
            due_date=date.today() + timedelta(days=3),
            status="not_started",
            user=user
        )

        def mock_get(*args, **kwargs):
            raise Exception("Database crash")

        monkeypatch.setattr(task.objects, "get", mock_get)

        response = auth_client.delete(f"{url}?task_id={t.id}")

        assert response.status_code == 500
        assert "Exception error" in response.json()["message"]
