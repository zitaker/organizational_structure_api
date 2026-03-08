"""Serializer for EmployeeModel."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel, EmployeeModel


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeModel with all fields."""

    department = serializers.PrimaryKeyRelatedField(
        label=_("Department"),
        queryset=DepartmentModel.objects.all(),
        required=True,
        allow_null=False,
    )

    full_name = serializers.CharField(
        label=_("Full name"),
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    position = serializers.CharField(
        label=_("Position"),
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    hired_at = serializers.DateField(
        label=_("Hired date"),
        help_text=_("Date when employee was hired"),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = EmployeeModel
        fields = ["id", "department", "full_name", "position", "hired_at", "created_at"]
        read_only_fields = ["id", "created_at"]


class EmployeeCreateSerializer(EmployeeSerializer):
    """Serializer for creating an employee."""

    department = None

    class Meta(EmployeeSerializer.Meta):
        fields = ["full_name", "position", "hired_at"]
