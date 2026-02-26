"""Service classes for Department business logic."""

import re
from typing import Any, Optional, Union

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, ValidationError

from src.apps.departments.models import DepartmentModel
from src.apps.departments.serializers.employee import EmployeeSerializer


class DepartmentValidator:
    """Validator for department data."""

    @staticmethod
    def validate_name_format(name: str) -> None:
        """
        Validate department name format.
        :param name: Department name to validate.
        :raises ValidationError: If name contains invalid characters.
        """
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]+$", name):
            raise ValidationError(_("Name can only contain letters and spaces."))

    @staticmethod
    def validate_unique_name_in_parent(
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

    @staticmethod
    def validate_no_self_parent(
        parent: DepartmentModel, instance: DepartmentModel
    ) -> None:
        """
        Validate that department cannot be parent of itself.
        :param parent: Proposed parent department.
        :param instance: Current department instance.
        :raises ValidationError: If parent is the same as instance.
        """
        if parent.pk == instance.pk:
            raise ValidationError({"parent": _("Department cannot be parent of self.")})

    @staticmethod
    def validate_no_cycle(parent: DepartmentModel, instance: DepartmentModel) -> None:
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


class DepartmentCreateUpdateService:
    """Service class for creating and updating departments."""

    validator = DepartmentValidator()

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
            self.validator.validate_name_format(name)

            if parent is not None:
                self.validator.validate_unique_name_in_parent(name, parent, instance)

        if parent and instance:
            self.validator.validate_no_self_parent(parent, instance)
            self.validator.validate_no_cycle(parent, instance)


class DepartmentTreeService:
    """Service class for building department tree structure."""

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

        children = getattr(department, "children").all()
        if not children.exists():
            return []

        result = []
        for child in children:
            child_data = {
                "id": child.pk,
                "name": child.name,
                "parent": child.parent_id,
                "created_at": child.created_at,
                "employees_count": child.employees.count(),
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
        children = getattr(department, "children").all()
        if not children.exists():
            return current_depth

        max_child_depth = current_depth
        for child in children:
            child_depth = self.get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth


class DepartmentQueryService:
    """Service class for department queries with parameters."""

    tree_service = DepartmentTreeService()

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
        requested_depth = self._validate_depth(depth, max_allowed_depth)

        if requested_depth == 0:
            children = []
        else:
            if requested_depth > 0:
                self._validate_depth_against_tree(department, requested_depth)
            children = self.tree_service.build_tree(
                department, max_depth=requested_depth
            )

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

    def _validate_depth(
        self, depth: Optional[Union[str, int]], max_allowed: int = 5
    ) -> int:
        """
        Validate and parse depth parameter.
        :param depth: Depth value (can be string from query param).
        :param max_allowed: Maximum allowed depth value.
        :return: Validated depth value.
        :raises ValidationError: If depth validation fails.
        """
        if depth is None:
            return 1

        try:
            depth_value = int(depth)
        except (ValueError, TypeError):
            raise ValidationError(_("Depth must be a valid integer."))

        if depth_value < 0:
            raise ValidationError(_("Depth must be 0 or positive integer."))
        if depth_value > max_allowed:
            raise ValidationError(
                _("Depth cannot exceed %(max)d.") % {"max": max_allowed}
            )

        return depth_value

    def _validate_depth_against_tree(
        self, department: DepartmentModel, requested_depth: int
    ) -> None:
        """
        Validate that requested depth does not exceed maximum available depth.
        :param department: The department to check depth against.
        :param requested_depth: The depth value requested.
        :raises ValidationError: If requested depth exceeds maximum available depth.
        """
        actual_depth = self.tree_service.get_max_depth(department)
        if requested_depth > actual_depth:
            raise ValidationError(
                _("Maximum available depth is %(max)d.") % {"max": actual_depth}
            )


class DepartmentEmployeeService:
    """Service class for department employee operations."""

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

        employees_queryset = getattr(department, "employees").all()

        if sort_by == "full_name":
            employees_queryset = employees_queryset.order_by("full_name")
        elif sort_by == "created_at":
            employees_queryset = employees_queryset.order_by("created_at")
        else:
            employees_queryset = employees_queryset.order_by("created_at")

        return EmployeeSerializer(employees_queryset, many=True).data  # type: ignore


class DepartmentDeleteService:
    """Service class for department deletion operations."""

    @staticmethod
    def delete_department_cascade(department: DepartmentModel) -> None:
        """
        Delete department with all its employees and child departments.
        :param department: Department to delete
        """
        department.delete()

    @staticmethod
    def delete_department_reassign(
        department: DepartmentModel, reassign_to_id: Optional[str]
    ) -> None:
        """
        Delete department and reassign its employees to another department.
        :param department: Department to delete
        :param reassign_to_id: ID of target department for employee reassignment
        :raises ValidationError: If reassign_to_id is missing
        or points to same department
        :raises NotFound: If target department doesn't exist
        """
        if not reassign_to_id:
            raise ValidationError(
                {
                    "reassign_to_department_id": _(
                        "This field is required when mode is 'reassign'."
                    )
                }
            )

        try:
            target_department = DepartmentModel.objects.get(id=reassign_to_id)
        except DepartmentModel.DoesNotExist:
            raise NotFound(_("Target department not found."))

        if target_department.pk == department.pk:
            raise ValidationError(
                {
                    "reassign_to_department_id": _(
                        "Cannot reassign employees to "
                        "the same department being deleted."
                    )
                }
            )

        with transaction.atomic():
            employees_manager = getattr(department, "employees")
            employees_manager.update(department=target_department)
            department.delete()

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
            self.delete_department_cascade(department)
        elif mode == "reassign":
            self.delete_department_reassign(department, reassign_to_id)
        else:
            raise ValidationError(
                {"mode": _("Mode must be either 'cascade' or 'reassign'.")}
            )
