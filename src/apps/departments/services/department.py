"""Service tree for Department business logic."""

from typing import Any, Dict, List, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel


class DepartmentTreeService:
    """Service class for Department tree operations."""

    def get_max_depth(self, department: DepartmentModel, current_depth: int = 1) -> int:
        """
        Calculate maximum depth of the department tree.
        :param department: The department to calculate depth for.
        :param current_depth: Current depth in recursion (default 1).
        :return: Maximum depth of the tree.
        """
        subdepartments = department.subdepartments.all()
        if not subdepartments.exists():
            return current_depth

        max_sub_depth = current_depth
        for sub in subdepartments:
            sub_depth = self.get_max_depth(sub, current_depth + 1)
            max_sub_depth = max(max_sub_depth, sub_depth)

        return max_sub_depth

    def build_subdepartment_tree(
        self,
        department: DepartmentModel,
        current_depth: int = 1,
        max_depth: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Recursively build subdepartment tree structure.
        :param department: The department to build tree for.
        :param current_depth: Current depth in recursion (default 1).
        :param max_depth: Maximum depth to traverse (None for unlimited).
        :return: List of subdepartment dictionaries with nested structure.
        """

        if max_depth is not None and current_depth > max_depth:
            return []

        subdepartments = department.subdepartments.all()
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
                "subdepartments": self.build_subdepartment_tree(
                    subdept, current_depth + 1, max_depth
                ),
            }
            result.append(subdept_data)

        return result

    def validate_depth(self, depth_param: Optional[str]) -> Optional[int]:
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

    def validate_depth_against_tree(
        self, department: DepartmentModel, requested_depth: int
    ) -> None:
        """
        Validate that requested depth does not exceed maximum available depth.
        :param department: The department to check depth against.
        :param requested_depth: The depth value requested by user.
        :raises ValidationError: If requested depth exceeds maximum available depth.
        """
        actual_depth = self.get_max_depth(department)
        if requested_depth > actual_depth:
            raise ValidationError(
                _("Maximum available depth is %(max)d.") % {"max": actual_depth}
            )
