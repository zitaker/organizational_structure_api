"""Serializer for DepartmentModel."""

import re
from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentModel with all fields."""

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

    def validate_name(self, value: str) -> str:
        """
        Name validation: only letters (Latin/Cyrillic),
        without numbers and special characters.
        """
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]+$", value):
            raise serializers.ValidationError(
                _("Name can only contain letters and spaces.")
            )

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Uniqueness of department name within the same parent department.
        Department cannot be parent of itself.
        No cycles in the tree (cannot move department into its own subtree).
        """
        name = attrs.get("name")
        parent = attrs.get("parent")

        if name and parent is not None:
            queryset = DepartmentModel.objects.filter(name=name, parent=parent)

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    {
                        "name": _(
                            "Department with this name already "
                            "exists in this parent department."
                        )
                    }
                )

        if parent and self.instance and parent.pk == self.instance.pk:
            raise serializers.ValidationError(
                {"parent": _("Department cannot be parent of self.")}
            )

        if parent and self.instance:
            current_parent = parent
            while current_parent:
                if current_parent.pk == self.instance.pk:
                    raise serializers.ValidationError(
                        {"parent": _("Cannot move department into its own subtree.")}
                    )
                current_parent = current_parent.parent
        return attrs

    def create(self, validated_data: dict[str, Any]) -> DepartmentModel:
        """Create and return a new department instance."""
        return super().create(validated_data)

    def update(
        self, instance: DepartmentModel, validated_data: dict[str, Any]
    ) -> DepartmentModel:
        """Update and return an existing department instance."""
        return super().update(instance, validated_data)
