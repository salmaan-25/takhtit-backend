from rest_framework import serializers
from .models import CustomUser, Project, Sprint, Ticket


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'key', 'description', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['id', 'name', 'project', 'start_date', 'end_date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Object-level validation — runs after individual field validation.
        Checks that start_date is not after end_date.
        """
        start = data.get('start_date')
        end = data.get('end_date')

        if start and end and start > end:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )
        return data

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'key', 'title', 'description',
            'project', 'sprint', 'reporter', 'assignee',
            'status', 'priority',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_status(self, value):
        """
        Field-level validation for 'status'.
        Runs automatically because the method is named validate_<fieldname>.
        """
        valid_statuses = ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        return value

    def validate_priority(self, value):
        """Field-level validation for 'priority'."""
        valid_priorities = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']
        if value not in valid_priorities:
            raise serializers.ValidationError(f"Invalid priority. Must be one of: {valid_priorities}")
        return value
