"""Service tree for Department business logic."""

import re
from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel


class DepartmentService:
    """Service class for Department operations."""

    def validate_department_name(self, name: str) -> None:
        """
        Validate department name format.
        :param name: Department name to validate.
        :raises ValidationError: If name contains invalid characters.
        """
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]+$", name):
            raise ValidationError(_("Name can only contain letters and spaces."))

    def validate_unique_name_in_parent(
        self,
        name: str,
        parent: Optional[DepartmentModel],
        instance: Optional[DepartmentModel] = None,
    ) -> None:
        """
        Validate uniqueness of department name within the same parent.
        :param name: Department name to check.
        :param parent: Parent department.
        :param instance: Current department instance for update operations.
        :raises ValidationError: If department with same name exists in parent.
        """
        queryset = DepartmentModel.objects.filter(name=name, parent=parent)

        if instance:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise ValidationError(
                {
                    "name": _(
                        "Department with this name already "
                        "exists in this parent department."
                    )
                }
            )

    def validate_no_self_parent(
        self, parent: DepartmentModel, instance: DepartmentModel
    ) -> None:
        """
        Validate that department cannot be parent of itself.
        :param parent: Proposed parent department.
        :param instance: Current department instance.
        :raises ValidationError: If parent is the same as instance.
        """
        if parent.pk == instance.pk:
            raise ValidationError({"parent": _("Department cannot be parent of self.")})

    def validate_no_cycle(
        self, parent: DepartmentModel, instance: DepartmentModel
    ) -> None:
        """
        Validate that moving department doesn't create a cycle.
        :param parent: Proposed parent department.
        :param instance: Current department instance being moved.
        :raises ValidationError: If moving would create a cycle.
        """
        current_parent = parent
        while current_parent:
            if current_parent.pk == instance.pk:
                raise ValidationError(
                    {"parent": _("Cannot move department into its own subtree.")}
                )
            current_parent = current_parent.parent

    def validate_department_data(
        self,
        name: Optional[str] = None,
        parent: Optional[DepartmentModel] = None,
        instance: Optional[DepartmentModel] = None,
    ) -> None:
        """
        Validate all department data.
        :param name: Department name to validate.
        :param parent: Parent department.
        :param instance: Current department instance for update operations.
        :raises ValidationError: If any validation fails.
        """
        if name:
            self.validate_department_name(name)

            if parent is not None:
                self.validate_unique_name_in_parent(name, parent, instance)

        if parent and instance:
            self.validate_no_self_parent(parent, instance)
            self.validate_no_cycle(parent, instance)


class DepartmentRetrieveService:
    """Service class for Department tree operations."""

    def get_department_tree(
        self,
        department: DepartmentModel,
        depth_param: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Get department tree with depth validation and building.
        :param department: The department to build tree for.
        :param depth_param: Raw depth parameter from request.
        :return: List of subdepartments with nested structure.
        :raises ValidationError: If depth validation fails.
        """
        max_depth = self._validate_depth(depth_param)

        if max_depth == 0:
            return []

        tree = self._build_department_tree(department, max_depth=max_depth)

        if max_depth and max_depth > 0:
            self._validate_depth_against_tree(department, max_depth)

        return tree

    def _validate_depth(self, depth_param: Optional[str]) -> Optional[int]:
        """
        Validate and parse depth parameter.
        :param depth_param: Raw depth parameter from request query string.
        :return: Parsed depth value or None if parameter not provided.
        """
        if depth_param is None:
            return None

        try:
            depth = int(depth_param)
            if depth < 0:
                raise ValidationError(_("Depth must be 0 or positive integer."))
            return depth
        except (ValueError, TypeError):
            raise ValidationError(_("Depth must be a valid integer."))

    def _build_department_tree(
        self,
        department: DepartmentModel,
        current_depth: int = 1,
        max_depth: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Recursively build subdepartment tree structure.
        :param department: The department to build tree for.
        :param current_depth: Current depth in recursion (default 1).
        :param max_depth: Maximum depth to traverse (None for unlimited).
        :return: List of subdepartment dictionaries with nested structure.
        """
        if max_depth is not None and current_depth > max_depth:
            return []

        subdepartments = department.subdepartments.all()  # type: ignore
        if not subdepartments.exists():
            return []

        result = []
        for subdept in subdepartments:
            subdept_data = {
                "id": subdept.id,
                "name": subdept.name,
                "parent": subdept.parent_id,
                "created_at": subdept.created_at,
                "employees_count": subdept.employees.count(),
                "subdepartments": self._build_department_tree(
                    subdept, current_depth + 1, max_depth
                ),
            }
            result.append(subdept_data)

        return result

    def _validate_depth_against_tree(
        self, department: DepartmentModel, requested_depth: int
    ) -> None:
        """
        Validate that requested depth does not exceed maximum available depth.
        :param department: The department to check depth against.
        :param requested_depth: The depth value requested by user.
        :raises ValidationError: If requested depth exceeds maximum available depth.
        """
        actual_depth = self._get_max_depth(department)
        if requested_depth > actual_depth:
            raise ValidationError(
                _("Maximum available depth is %(max)d.") % {"max": actual_depth}
            )

    def _get_max_depth(
        self, department: DepartmentModel, current_depth: int = 1
    ) -> int:
        """
        Calculate maximum depth of the department tree.
        :param department: The department to calculate depth for.
        :param current_depth: Current depth in recursion (default 1).
        :return: Maximum depth of the tree.
        """
        subdepartments = department.subdepartments.all()  # type: ignore
        if not subdepartments.exists():
            return current_depth

        max_sub_depth = current_depth
        for sub in subdepartments:
            sub_depth = self._get_max_depth(sub, current_depth + 1)
            max_sub_depth = max(max_sub_depth, sub_depth)

        return max_sub_depth
