"""Serializer for EmployeeModel."""

from datetime import date
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel, EmployeeModel


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeModel with all fields."""

    department = serializers.PrimaryKeyRelatedField(
        label=_("Department"),
        help_text=_("Department where employee works"),
        queryset=DepartmentModel.objects.all(),
        required=True,
        allow_null=False,
        error_messages={
            "does_not_exist": _("Department with id {pk_value} does not exist."),
            "required": _("Department is required."),
        },
    )

    full_name = serializers.CharField(
        label=_("Full name"),
        help_text=_("Employee full name"),
        min_length=2,
        max_length=200,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "blank": _("Full name cannot be empty."),
            "required": _("Full name is required."),
            "min_length": _("Full name must be at least 2 characters long."),
            "max_length": _("Full name must be no more than 200 characters long."),
        },
    )

    position = serializers.CharField(
        label=_("Position"),
        help_text=_("Employee position"),
        min_length=2,
        max_length=200,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "blank": _("Position cannot be empty."),
            "required": _("Position is required."),
            "min_length": _("Position must be at least 2 characters long."),
            "max_length": _("Position must be no more than 200 characters long."),
        },
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

    def validate_full_name(self, value: str) -> str:
        """
        Full name check: must be formatted correctly.
        """
        if len(value.split()) < 2:
            raise serializers.ValidationError(
                _("Please enter both first name and last name.")
            )

        return value

    def validate_hired_at(self, value):
        """
        Validate that hire date is not earlier than 2010-01-01.
        """
        if value:
            min_date = date(2010, 1, 1)
            if value < min_date:
                raise serializers.ValidationError(
                    _("Hire date cannot be earlier than 2010-01-01.")
                )
        return value

    def create(self, validated_data: dict[str, Any]) -> EmployeeModel:
        """Create and return a new employee instance."""
        return super().create(validated_data)

    def update(
        self, instance: EmployeeModel, validated_data: dict[str, Any]
    ) -> EmployeeModel:
        """Update and return an existing employee instance."""
        return super().update(instance, validated_data)
