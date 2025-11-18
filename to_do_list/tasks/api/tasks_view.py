from rest_framework import viewsets
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from utils.global_utils import create_response

from tasks.serializers import TaskListSerializer, TaskCreateSerializer
from tasks.models import task
from accounts.models import User

from datetime import date, timedelta, datetime

class TaskView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):

        title = request.data.get('title')
        due_date = request.data.get('due_date')

        request.data['user'] = request.user.id

        if task.objects.filter(title=title, user=request.user).exists():
            return create_response(
                status = http_status.HTTP_400_BAD_REQUEST,
                message=f"Task {title} already exists."
            )
        
        if due_date:
            tomorrow = date.today() + timedelta(days=1)
            if datetime.strptime(due_date, "%Y-%m-%d").date() < tomorrow:
                return create_response(
                    status=http_status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid Due Date"
                )

        try:
            serializer = TaskCreateSerializer(data=request.data)
            if serializer.is_valid():
                post = serializer.save()
                return create_response(
                    message="Post created successfully.",
                    result=TaskListSerializer(post).data,
                    status=http_status.HTTP_201_CREATED
                )

            return create_response(
                message=serializer.errors,
                status=http_status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
    def list(self, request):
        try:
            status = request.data.get('status')

            if status not in dict(task.STATUS_CHOICES).keys() or status != 'all':
                return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message=f"Invalid Status"
            )
            
            if status == 'all':
                tasks = task.objects.filter(user=request.user)
            else:
                tasks = task.objects.filter(status=status, user=request.user)

            serializer = TaskListSerializer(tasks, many=True)
            return create_response(result=serializer.data)

        except Exception as e:
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
    def retrieve(self, request):
        try:
            id = request.query_params.get('task_id')
            task_obj = task.objects.get(id=id, is_deleted=False)
            serializer = TaskListSerializer(task_obj)
            return create_response(
                status=http_status.HTTP_200_OK,
                message="Task found successfully.",
                result=serializer.data
            )
        except task.DoesNotExist:
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )

    def update(self, request):
        try:
            id = request.query_params.get('task_id')
            task_obj = task.objects.get(id=id, user=request.user, is_deleted=False)
        except task.DoesNotExist:
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )
        
        title = request.data.get("title")
        due_date = request.data.get("due_date")
        status = request.data.get("status")
        
        if title and task.objects.filter(title=title).exists():
            return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message="Title Already exists."
            )
        
        if status not in dict(task.STATUS_CHOICES).keys():
                return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message=f"Invalid Status"
            )
        
        if due_date:
            tomorrow = date.today() + timedelta(days=1)
            if datetime.strptime(due_date, "%Y-%m-%d").date() < tomorrow:
                return create_response(
                    status=http_status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid Due Date"
                )

        data = request.data.copy()
        serializer = TaskCreateSerializer(task_obj, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return create_response(
                message="Task updated successfully.",
                result=serializer.data
            )
        else:
            return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message=serializer.errors
            )

    def destroy(self, request):
        try:
            id = request.query_params.get('task_id')
            task_obj = task.objects.get(id=id, is_deleted=False)
            task_obj.is_deleted = True
            return create_response(
                message="Task deleted successfully."
            )
        except task.DoesNotExist:
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )
        except Exception as e:
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
