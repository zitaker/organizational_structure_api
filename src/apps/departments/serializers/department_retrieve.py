"""Serializers for Department tree structure."""

from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel
from src.apps.departments.services.department import DepartmentRetrieveService


class DepartmentRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed department information with tree structure.
    """

    service = DepartmentRetrieveService()

    children = serializers.SerializerMethodField(
        label=_("Children"),
        help_text=_("Nested subdepartments"),
    )

    employees = serializers.SerializerMethodField(
        label=_("Employees"),
        help_text=_("Employees of the department"),
        read_only=True,
    )

    employees_count = serializers.IntegerField(
        label=_("Employees count"),
        help_text=_("Number of employees in the department"),
        read_only=True,
    )

    class Meta:
        model = DepartmentModel
        fields = [
            "id",
            "name",
            "parent",
            "created_at",
            "employees_count",
            "employees",
            "children",
        ]

    def get_children(self, obj: DepartmentModel) -> list[dict[str, Any]]:
        """Get children departments tree."""
        request = self.context.get("request")
        return self.service.script_distributor(obj, request, field="children")

    def get_employees(self, obj: DepartmentModel) -> list:
        """Get employees with filtering and sorting."""
        request = self.context.get("request")
        return self.service.script_distributor(obj, request, field="employees")
