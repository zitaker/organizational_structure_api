"""Serializers for Department tree structure."""

from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel
from src.apps.departments.services.department import (
    DepartmentEmployeeService,
    DepartmentQueryService,
)


class DepartmentRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed department information with tree structure.
    """

    query_service = DepartmentQueryService()
    employee_service = DepartmentEmployeeService()

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
        depth = None
        if request:
            depth_param = request.query_params.get("depth")
            depth = depth_param

        tree_data = self.query_service.get_department_with_children(obj, depth=depth)
        return tree_data.get("children", [])

    def get_employees(self, obj: DepartmentModel) -> list:
        """Get employees with filtering and sorting."""
        request = self.context.get("request")

        include_employees = True
        sort_by = "created_at"

        if request:
            include_param = request.query_params.get(
                "include_employees", "true"
            ).lower()
            include_employees = include_param == "true"
            sort_by = request.query_params.get("sort_employees_by", "created_at")

        return self.employee_service.get_employees(
            obj, include_employees=include_employees, sort_by=sort_by
        )
