"""Serializers for Department tree structure."""

from typing import Any

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel
from src.apps.departments.serializers.employee import EmployeeSerializer
from src.apps.departments.services.department import DepartmentTreeService


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed department information with tree structure.
    """

    subdepartments = serializers.SerializerMethodField(
        label=_("Subdepartments"),
        help_text=_("Nested subdepartments"),
    )
    employees = EmployeeSerializer(
        label=_("Employees"),
        help_text=_("Employees of the department"),
        many=True,
        read_only=True,
        source="employees.all",
    )
    employees_count = serializers.IntegerField(
        label=_("Employees count"),
        help_text=_("Number of employees in the department"),
        source="employees.count",
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
            "subdepartments",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = DepartmentTreeService()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_subdepartments(self, obj: DepartmentModel) -> list[dict[str, Any]]:
        """
        Get subdepartments tree with depth limitation.
        :param obj: DepartmentModel instance for which to get subdepartments.
        :return: List of subdepartments with nested structure.
        """
        request = self.context.get("request")
        depth_param = request.query_params.get("depth") if request else None
        max_depth = self.service.validate_depth(depth_param)
        if max_depth == 0:
            return []
        tree = self.service.build_subdepartment_tree(obj, max_depth=max_depth)
        if max_depth and max_depth > 0:
            self.service.validate_depth_against_tree(obj, max_depth)
        return tree
