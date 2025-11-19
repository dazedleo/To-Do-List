import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tasks.models import task
from datetime import date, timedelta


@pytest.fixture
def url():
    return reverse("update_task")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestTaskUpdateAPI:

    def test_success_update(self, auth_client, user, url):
        t = task.objects.create(
            title="Old",
            due_date=date.today() + timedelta(days=3),
            status="in_progress",
            user=user
        )

        payload = {
            "title": "Updated",
            "due_date": (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "status": "in_progress",
        }

        response = auth_client.put(f"{url}?task_id={t.id}", payload, format="json")

        assert response.status_code == 200
        assert response.json()["message"] == "Task updated successfully."

    def test_task_not_found(self, auth_client, url):
        uuid_not_exists = "00000000-0000-0000-0000-000000000000"

        response = auth_client.put(
            f"{url}?task_id={uuid_not_exists}",
            {
                "title": "X",
                "due_date": (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "not_started", 
            },
            format="json"
        )

        assert response.status_code == 404
        assert response.json()["message"] == "Task not found."

    def test_invalid_status(self, auth_client, user, url):
        t = task.objects.create(
            title="Task",
            due_date=date.today() + timedelta(days=3),
            status="not_started", 
            user=user
        )

        response = auth_client.put(
            f"{url}?task_id={t.id}",
            {
                "title": "New",
                "due_date": (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "WRONG", 
            },
            format="json"
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Invalid Status"

    def test_invalid_due_date(self, auth_client, user, url):
        t = task.objects.create(
            title="TaskX",
            due_date=date.today() + timedelta(days=3),
            status="not_started", 
            user=user
        )

        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        response = auth_client.put(
            f"{url}?task_id={t.id}",
            {
                "title": "New",
                "due_date": yesterday,  
                "status": "not_started", 
            },
            format="json"
        )

        assert response.status_code == 400
        assert response.json()["message"] == "Invalid Due Date"

    def test_serializer_invalid(self, auth_client, user, url):
        t = task.objects.create(
            title="TaskX",
            due_date=date.today() + timedelta(days=3),
            status="not_started",
            user=user
        )

        response = auth_client.put(
            f"{url}?task_id={t.id}",
            {
                "title": "",  
                "due_date": (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "not_started", 
            },
            format="json"
        )

        assert response.status_code == 400
        assert "title" in str(response.json()["message"])

    def test_internal_server_error(self, auth_client, user, url, monkeypatch):
        t = task.objects.create(
            title="TaskX",
            due_date=date.today() + timedelta(days=3),
            status="not_started",
            user=user
        )

        def mock_get(*args, **kwargs):
            raise Exception("Database crash")

        monkeypatch.setattr(task.objects, "get", mock_get)

        response = auth_client.put(
            f"{url}?task_id={t.id}",
            {
                "title": "New",
                "due_date": (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "not_started",
            },
            format="json"
        )

        assert response.status_code == 500
        assert "Exception error" in response.json()["message"]
