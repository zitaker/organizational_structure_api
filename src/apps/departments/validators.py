"""Validation for application development departments."""

import re

from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel


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
