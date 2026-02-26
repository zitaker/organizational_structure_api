"""Service tree for Department business logic."""

import re
from typing import Any, Optional

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, ValidationError

from src.apps.departments.models import DepartmentModel
from src.apps.departments.serializers.employee import EmployeeSerializer


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

    def script_distributor(
        self,
        department: DepartmentModel,
        request: Optional[Any] = None,
        field: Optional[str] = None,
    ) -> Any:
        """
        Distribute requests to appropriate methods based on field parameter.
        :param department: DepartmentModel instance
        :param request: Request object for query params
        :param field: Which field data to return ("children" or "employees")
        :return: Data for the requested field
        """
        if field == "children":
            return self._get_children(department, request)
        elif field == "employees":
            return self._get_employees(department, request)
        return []

    def _get_children(
        self,
        department: DepartmentModel,
        request: Optional[Any] = None,
    ) -> list[dict[str, Any]]:
        """
        Get children departments tree with depth limitation.
        :param department: The department to build tree for.
        :param request: Request object for query params.
        :return: List of children departments with nested structure.
        """
        depth_param = request.query_params.get("depth") if request else None
        max_depth = self._validate_depth(depth_param, max_allowed=5)

        if max_depth == 0:
            return []

        tree = self._build_department_tree(department, max_depth=max_depth)

        if max_depth and max_depth > 0:
            self._validate_depth_against_tree(department, max_depth)

        return tree

    def _get_employees(
        self,
        department: DepartmentModel,
        request: Optional[Any] = None,
    ) -> list:
        """
        Get employees for department with filtering and sorting.
        :param department: DepartmentModel instance
        :param request: Request object for query params
        :return: List of serialized employees
        """
        if not request:
            employees_queryset = getattr(department, "employees").all()
            serializer = EmployeeSerializer(employees_queryset, many=True)
            return serializer.data  # type: ignore

        include_employees = request.query_params.get(
            "include_employees", "true"
        ).lower()

        if include_employees == "false":
            return []

        sort_by = request.query_params.get("sort_employees_by", "created_at")
        if sort_by not in ["created_at", "full_name"]:
            sort_by = "created_at"

        employees = getattr(department, "employees").all().order_by(sort_by)
        return EmployeeSerializer(employees, many=True).data  # type: ignore

    def _validate_depth(self, depth_param: Optional[str], max_allowed: int = 5) -> int:
        """
        Validate and parse depth parameter.
        :param depth_param: Raw depth parameter from request query string.
        :param max_allowed: Maximum allowed depth value.
        :return: Parsed depth value or 1 if parameter not provided.
        :raises ValidationError: If depth validation fails.
        """
        if depth_param is None:
            return 1

        try:
            depth = int(depth_param)
            if depth < 0:
                raise ValidationError(_("Depth must be 0 or positive integer."))
            if depth > max_allowed:
                raise ValidationError(_(f"Depth cannot exceed {max_allowed}."))
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
                "children": self._build_department_tree(
                    child, current_depth + 1, max_depth
                ),
            }
            result.append(child_data)

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
        children = getattr(department, "children").all()
        if not children.exists():
            return current_depth

        max_child_depth = current_depth
        for child in children:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth


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
