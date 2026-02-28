"""Serializer for DepartmentModel."""

from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel
from src.apps.departments.validators import DepartmentValidator


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentModel with all fields."""

    validator = DepartmentValidator()

    name = serializers.CharField(
        label=_("Name"),
        help_text=_("Department name"),
        min_length=2,
        max_length=200,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        error_messages={
            "blank": _("Name cannot be empty."),
            "required": _("Name is required."),
            "min_length": _("Name must be at least 2 character long."),
            "max_length": _("Name must be no more than 200 characters long."),
        },
    )

    parent = serializers.PrimaryKeyRelatedField(
        label=_("Parent id"),
        help_text=_("Parent department ID"),
        queryset=DepartmentModel.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": _("Parent department with id {pk_value} does not exist."),
            "incorrect_type": _("Incorrect type. Expected department ID value."),
        },
    )

    class Meta:
        model = DepartmentModel
        fields = ["id", "name", "parent", "created_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate department data using service layer.
        """
        self.validator.validate_department_data(
            name=attrs.get("name"), parent=attrs.get("parent"), instance=self.instance
        )
        return attrs
