import pytest
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from tasks.models import task
from tasks.serializers import TaskListSerializer


@pytest.mark.django_db
class TestTaskListAPI:

    @pytest.fixture
    def url(self):
        return reverse("list_of_task")

    def test_success_fetch_all(self, auth_client, user, url):
        t1 = task.objects.create(
            title="Task 1", description="Desc", status="not_started", user=user
        )
        t2 = task.objects.create(
            title="Task 2", description="Desc", status="completed", user=user
        )

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "tasks fetched successfully"

        result = response.json()["result"]
        assert len(result) == 2

        expected = TaskListSerializer([t1, t2], many=True).data
        assert result == expected

    def test_success_fetch_filtered_status(self, auth_client, user, url):
        task.objects.create(
            title="Task 1", description="Desc", status="not_started", user=user
        )
        task.objects.create(
            title="Task 2", description="Desc", status="completed", user=user
        )

        response = auth_client.get(url + "?status=completed")

        assert response.status_code == status.HTTP_200_OK

        result = response.json()["result"]
        assert len(result) == 1
        assert result[0]["status"] == "completed"

    def test_invalid_status(self, auth_client, url):
        response = auth_client.get(url + "?status=invalid_status")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid Status" in response.json()["message"]

    def test_internal_server_error(self, auth_client, url, monkeypatch):
        def explode(*args, **kwargs):
            raise Exception("Forced Crash")

        monkeypatch.setattr(
            "tasks.api.tasks_view.task.objects.filter",
            explode
        )

        response = auth_client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Exception error" in response.json()["message"]
