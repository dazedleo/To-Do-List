from rest_framework import serializers

from tasks.models import task

from datetime import date

class TaskListSerializer(serializers.ModelSerializer):

    class Meta:
        model = task
        fields = ["id", "title", "description", "due_date", "status"]

class TaskCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = task
        fields = ['user', 'title', 'description', 'due_date', 'status']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Invalid Due Date")
        return value

    def validate_status(self, value):
        valid_status = ["not_started", "in_progress", "completed", "canceled"]
        if value not in valid_status:
            raise serializers.ValidationError("Invalid Status")
        return value