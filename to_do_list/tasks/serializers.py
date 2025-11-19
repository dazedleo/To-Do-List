from rest_framework import serializers

from tasks.models import task

class TaskListSerializer(serializers.ModelSerializer):

    class Meta:
        model = task
        fields = ["id", "title", "description", "due_date", "status"]

class TaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = task
        fields = ['user', 'title', 'description', 'due_date', 'status']