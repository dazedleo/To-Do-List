from rest_framework import viewsets
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated

from utils.global_utils import create_response

from tasks.serializers import TaskListSerializer, TaskCreateSerializer
from tasks.models import task

from datetime import date, timedelta, datetime

import logging

from django.views.generic import TemplateView

logger = logging.getLogger(__name__)

class TaskView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        logger.info("Create task request by user_id=%s with data=%s", request.user.id, request.data)

        title = request.data.get('title')
        due_date = request.data.get('due_date')
        status = request.data.get('status')

        request.data['user'] = request.user.id

        if status not in dict(task.STATUS_CHOICES).keys():
                logger.warning("Invalid status value '%s' on task list by user_id=%s", status, request.user.id)
                return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message=f"Invalid Status - {status}"
            )

        if task.objects.filter(title=title, user=request.user).exists():
            logger.warning("Task creation failed - duplicate title '%s' by user_id=%s", title, request.user.id)
            return create_response(
                status = http_status.HTTP_400_BAD_REQUEST,
                message=f"Task {title} already exists."
            )
        
        if due_date:
            tomorrow = date.today() + timedelta(days=1)
            if datetime.strptime(due_date, "%Y-%m-%d").date() < tomorrow:
                logger.warning("Task creation failed - invalid due date '%s' by user_id=%s", due_date, request.user.id)
                return create_response(
                    status=http_status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid Due Date"
                )

        try:
            serializer = TaskCreateSerializer(data=request.data)
            if serializer.is_valid():
                post = serializer.save()
                logger.info("Task created successfully with id=%s by user_id=%s", post.id, request.user.id)
                return create_response(
                    message="Post created successfully.",
                    result=TaskListSerializer(post).data,
                    status=http_status.HTTP_201_CREATED
                )
            
            logger.warning("Task creation serializer invalid: %s by user_id=%s", serializer.errors, request.user.id)
            return create_response(
                message=serializer.errors,
                status=http_status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Exception on task create by user_id=%s: %s", request.user.id, e, exc_info=True)
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
    def list(self, request):
        logger.info("List tasks request by user_id=%s with data=%s", request.user.id, request.data)
        try:
            status = request.query_params.get('status', 'all')

            if status not in dict(task.STATUS_CHOICES).keys() and status != 'all':
                logger.warning("Invalid status value '%s' on task list by user_id=%s", status, request.user.id)
                return create_response(
                status=http_status.HTTP_400_BAD_REQUEST,
                message=f"Invalid Status - {status}"
            )
            
            if status == 'all':
                tasks = task.objects.filter(user=request.user, is_deleted=False)
            else:
                tasks = task.objects.filter(status=status, user=request.user, is_deleted=False)

            serializer = TaskListSerializer(tasks, many=True)
            logger.info("Listed %d tasks for user_id=%s with status=%s", len(tasks), request.user.id, status)
            return create_response(
                status=http_status.HTTP_200_OK,
                result=serializer.data,
                message="tasks fetched successfully"
            )

        except Exception as e:
            logger.error("Exception on task list for user_id=%s: %s", request.user.id, e, exc_info=True)
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
    def retrieve(self, request):
        try:
            id = request.query_params.get('task_id')
            logger.info("Retrieve task request task_id=%s by user_id=%s", id, request.user.id)
            task_obj = task.objects.get(id=id, user=request.user, is_deleted=False)
            serializer = TaskListSerializer(task_obj)
            logger.info("Task found task_id=%s by user_id=%s", id, request.user.id)
            return create_response(
                status=http_status.HTTP_200_OK,
                message="Task found successfully.",
                result=serializer.data
            )
        except task.DoesNotExist:
            logger.warning("Task not found task_id=%s by user_id=%s", id, request.user.id)
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )
        
        except Exception as e:
            logger.error("Exception on task retrieve for user_id=%s: %s", request.user.id, e, exc_info=True)
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )

    def update(self, request):
        try:
            id = request.query_params.get('task_id')
            logger.info("Update task request task_id=%s by user_id=%s with data=%s", id, request.user.id, request.data)
            task_obj = task.objects.get(id=id, user=request.user, is_deleted=False)
        
        
            title = request.data.get("title")
            due_date = request.data.get("due_date")
            status = request.data.get("status")
            description = request.data.get("description")
            

            if not description:
                request.data['description'] = task_obj.description
            
            if status not in dict(task.STATUS_CHOICES).keys():
                    logger.warning("Invalid status '%s' for task update task_id=%s by user_id=%s", status, id, request.user.id)
                    return create_response(
                    status=http_status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid Status"
                )
            
            if due_date:
                tomorrow = date.today() + timedelta(days=1)
                if datetime.strptime(due_date, "%Y-%m-%d").date() < tomorrow:
                    logger.warning("Invalid due date '%s' for task update task_id=%s by user_id=%s", due_date, id, request.user.id)
                    return create_response(
                        status=http_status.HTTP_400_BAD_REQUEST,
                        message=f"Invalid Due Date"
                    )

            data = request.data.copy()
            serializer = TaskCreateSerializer(task_obj, data=data, partial=False)
            if serializer.is_valid():
                serializer.save()
                logger.info("Task updated successfully task_id=%s by user_id=%s", id, request.user.id)
                return create_response(
                    status=http_status.HTTP_200_OK,
                    message="Task updated successfully.",
                    result=serializer.data
                )
            else:
                logger.warning("Task update serializer invalid error task_id=%s by user_id=%s: %s", id, request.user.id, serializer.errors)
                return create_response(
                    status=http_status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors
                )
            
        except task.DoesNotExist:
            logger.warning("Task to update not found task_id=%s by user_id=%s", id, request.user.id)
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )
        
        except Exception as e:
            logger.error("Exception on task updation task_id=%s by user_id=%s: %s", id, request.user.id, e, exc_info=True)
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )

    def destroy(self, request):
        try:
            id = request.query_params.get('task_id')
            logger.info("Delete task request task_id=%s by user_id=%s", id, request.user.id)
            task_obj = task.objects.get(id=id, user=request.user, is_deleted=False)
            task_obj.is_deleted = True
            task_obj.save()
            
            logger.info("Task deleted successfully task_id=%s by user_id=%s", id, request.user.id)
            return create_response(
                status=http_status.HTTP_200_OK,
                message="Task deleted successfully.",
                result={}
            )
        
        except task.DoesNotExist:
            logger.warning("Task to delete not found task_id=%s by user_id=%s", id, request.user.id)
            return create_response(
                status=http_status.HTTP_404_NOT_FOUND,
                message="Task not found."
            )
        
        except Exception as e:
            logger.error("Exception on task delete task_id=%s by user_id=%s: %s", id, request.user.id, e, exc_info=True)
            return create_response(
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Exception error : {e}"
            )
        
class IndexView(TemplateView):
    template_name = "index.html"