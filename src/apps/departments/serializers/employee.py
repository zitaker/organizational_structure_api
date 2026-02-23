"""Serializer for EmployeeModel."""

from rest_framework import serializers

from src.apps.departments.models import EmployeeModel


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeModel with all fields."""

    class Meta:
        model = EmployeeModel
        fields = "__all__"
