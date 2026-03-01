"""Service classes for Department business logic."""

from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel
from src.apps.departments.repositories import DepartmentDatabase
from src.apps.departments.serializers.employee import EmployeeSerializer
from src.apps.departments.validators import DepartmentValidator


class DepartmentTreeService:
    """Service class for building department tree structure."""

    database = DepartmentDatabase()

    def build_tree(
        self,
        department: DepartmentModel,
        current_depth: int = 1,
        max_depth: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Recursively build children department tree structure.
        :param department: The department to build tree for.
        :param current_depth: Current depth in recursion (default 1).
        :param max_depth: Maximum depth to traverse.
        :return: List of children department dictionaries with nested structure.
        """
        if max_depth is not None and current_depth > max_depth:
            return []

        children = self.database.get_children(department)
        if not children:
            return []

        result = []
        for child in children:
            child_data = {
                "id": child.pk,
                "name": child.name,
                "parent": getattr(child, "parent_id", None),
                "created_at": child.created_at,
                "employees_count": self.database.get_employees_count(child),
                "children": self.build_tree(child, current_depth + 1, max_depth),
            }
            result.append(child_data)

        return result

    def get_max_depth(self, department: DepartmentModel, current_depth: int = 1) -> int:
        """
        Calculate maximum depth of the department tree.
        :param department: The department to calculate depth for.
        :param current_depth: Current depth in recursion (default 1).
        :return: Maximum depth of the tree.
        """

        children = self.database.get_children(department)
        if not children:
            return current_depth

        max_child_depth = current_depth
        for child in children:
            child_depth = self.get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth


class DepartmentQueryService:
    """Service class for department queries with parameters."""

    service = DepartmentTreeService()
    validator = DepartmentValidator()

    def get_department_with_children(
        self,
        department: DepartmentModel,
        depth: Optional[int] = None,
        max_allowed_depth: int = 5,
    ) -> dict[str, Any]:
        """
        Get department with its children tree.
        :param department: The department instance.
        :param depth: Requested depth (None for default 1).
        :param max_allowed_depth: Maximum allowed depth.
        :return: Department data with children tree.
        :raises ValidationError: If depth validation fails.
        """
        requested_depth = self.validator.validate_depth(depth, max_allowed_depth)

        if requested_depth == 0:
            children = []
        else:
            if requested_depth > 0:
                self._validate_depth_against_tree(department, requested_depth)
            children = self.service.build_tree(department, max_depth=requested_depth)

        employees_manager = getattr(department, "employees", None)
        employees_count = (
            employees_manager.count() if employees_manager is not None else 0
        )

        return {
            "id": department.pk,
            "name": department.name,
            "parent": getattr(department, "parent_id", None),
            "created_at": department.created_at,
            "employees_count": employees_count,
            "children": children,
        }

    def _validate_depth_against_tree(
        self, department: DepartmentModel, requested_depth: int
    ) -> None:
        """
        Validate that requested depth does not exceed maximum available depth.
        :param department: The department to check depth against.
        :param requested_depth: The depth value requested.
        :raises ValidationError: If requested depth exceeds maximum available depth.
        """
        actual_depth = self.service.get_max_depth(department)
        if requested_depth > actual_depth:
            raise ValidationError(
                _("Maximum available depth is %(max)d.") % {"max": actual_depth}
            )


class DepartmentEmployeeService:
    """Service class for department employee operations."""

    serializer = EmployeeSerializer
    database = DepartmentDatabase()

    def get_employees(
        self,
        department: DepartmentModel,
        include_employees: bool = True,
        sort_by: str = "created_at",
    ) -> list:
        """
        Get employees for department with filtering and sorting.
        :param department: DepartmentModel instance.
        :param include_employees: Whether to include employees.
        :param sort_by: Field to sort employees by.
        :return: List of serialized employees.
        """
        if not include_employees:
            return []

        employees = self.database.get_sorted_employees(department, sort_by)

        return self.serializer(employees, many=True).data  # type: ignore


class DepartmentDeleteService:
    """Service class for department deletion operations."""

    database = DepartmentDatabase()

    def delete_department_reassign(
        self, department: DepartmentModel, reassign_to_id: Optional[str]
    ) -> None:
        """
        Delete department and reassign its employees to another department.
        :param department: Department to delete
        :param reassign_to_id: ID of target department for employee reassignment
        :raises ValidationError: If reassign_to_id is missing
        or points to same department
        :raises NotFound: If target department doesn't exist
        """
        if reassign_to_id is None:
            raise ValidationError(
                {
                    "reassign_to_department_id": _(
                        "This field is required when mode is 'reassign'."
                    )
                }
            )

        target_department: DepartmentModel = self.database.get_target_department(
            reassign_to_id
        )

        if target_department.pk == department.pk:
            raise ValidationError(
                {
                    "reassign_to_department_id": _(
                        "It is not possible to transfer employees to "
                        "the same department that is being abolished."
                    )
                }
            )

        self.database.reassign_and_delete(department, target_department)

    def delete_department(
        self,
        department: DepartmentModel,
        mode: str,
        reassign_to_id: Optional[str] = None,
    ) -> None:
        """
        Delete department based on specified mode.
        :param department: Department to delete
        :param mode: Delete mode ('cascade' or 'reassign')
        :param reassign_to_id: Target department ID for reassign mode
        :raises ValidationError: If mode is invalid or parameters are missing
        """
        if mode == "cascade":
            self.database.delete_department_cascade(department)
        elif mode == "reassign":
            self.delete_department_reassign(department, reassign_to_id)
