"""Serializer for DepartmentModel."""

from rest_framework import serializers

from src.apps.departments.models import DepartmentModel


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentModel with all fields."""

    class Meta:
        model = DepartmentModel
        fields = "__all__"
