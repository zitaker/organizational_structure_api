"""Validation for application development departments."""

import re
from datetime import date
from typing import Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel


class DepartmentValidator:
    """Validator for department data."""

    model = DepartmentModel

    @staticmethod
    def _validate_name_format(name: str) -> None:
        """
        Validate department name format.
        :param name: Department name to validate.
        :raises ValidationError: If name contains invalid characters.
        """
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s]+$", name):
            raise ValidationError(
                {"name": _("Name can only contain letters and spaces.")}
            )

    def _validate_unique_name_in_parent(
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
        queryset = self.model.objects.filter(name=name, parent=parent)

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
    def _validate_no_self_parent(
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
    def _validate_no_cycle(parent: DepartmentModel, instance: DepartmentModel) -> None:
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
            self._validate_name_format(name)
            self._validate_unique_name_in_parent(name, parent, instance)

        if parent and instance:
            self._validate_no_self_parent(parent, instance)
            self._validate_no_cycle(parent, instance)

    @staticmethod
    def validate_depth(depth: Optional[Union[str, int]], max_allowed: int = 5) -> int:
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


class EmployeeValidator:
    """Validator for employee data."""

    def _validate_full_name_format(self, full_name: str) -> None:
        """
        Validate employee full name format.
        :param full_name: Full name to validate.
        :raises ValidationError: If name doesn't contain both first and last name.
        """
        if len(full_name.split()) < 2:
            raise ValidationError(
                {"full_name": _("Please enter both first name and last name.")}
            )

    @staticmethod
    def _validate_hire_date(hired_at: Optional[Union[date, str]]) -> None:
        """
        Validate that hire date is not earlier than 2010-01-01.
        :param hired_at: Hire date to validate (can be string or date)
        :raises ValidationError: If date is earlier than 2010-01-01 or invalid format.
        """
        if hired_at:
            if isinstance(hired_at, str):
                try:
                    hired_at = date.fromisoformat(hired_at)
                except ValueError:
                    raise ValidationError(
                        {"hired_at": _("Invalid date format. Use YYYY-MM-DD.")}
                    )

            min_date = date(2010, 1, 1)
            if hired_at < min_date:
                raise ValidationError(
                    {"hired_at": _("Hire date cannot be earlier than 2010-01-01.")}
                )

    def validate_employee_data(
        self,
        full_name: Optional[str] = None,
        hired_at: Optional[Union[date, str]] = None,
    ) -> None:
        """
        Validate all employee data.
        :param full_name: Employee full name to validate.
        :param hired_at: Hire date to validate.
        :raises ValidationError: If any validation fails.
        """
        if full_name:
            self._validate_full_name_format(full_name)

        if hired_at:
            self._validate_hire_date(hired_at)
