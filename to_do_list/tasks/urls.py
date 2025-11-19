from django.urls import path, include
from tasks.api.tasks_view import TaskView


urlpatterns = [
    path("create-task/", TaskView.as_view({"post":"create"}), name="create_task"),
    path("retrieve-task/", TaskView.as_view({"get":"retrieve"}), name="retrieve_task"),
    path("list-of-task/", TaskView.as_view({"get":"list"}), name="list_of_task"),
    path("update-task/", TaskView.as_view({"put":"update"}), name="update_task"),
    path("destroy-task/", TaskView.as_view({"delete":"destroy"}), name="destroy_task"),
]
