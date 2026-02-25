"""Service for Employee business logic."""

from datetime import date
from typing import Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.models import DepartmentModel, EmployeeModel


class EmployeeService:
    """Service class for Employee operations."""

    def validate_full_name_format(self, full_name: str) -> None:
        """
        Validate employee full name format.
        :param full_name: Full name to validate.
        :raises ValidationError: If name doesn't contain both first and last name.
        """
        if len(full_name.split()) < 2:
            raise ValidationError(_("Please enter both first name and last name."))

    def validate_hire_date(self, hired_at: Optional[Union[date, str]]) -> None:
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
                raise ValidationError(_("Hire date cannot be earlier than 2010-01-01."))

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
            self.validate_full_name_format(full_name)

        if hired_at:
            self.validate_hire_date(hired_at)

    def create_employee(
        self, department: DepartmentModel, **employee_kwargs
    ) -> EmployeeModel:
        """
        Create a new employee.
        :param department: Department instance
        :param employee_kwargs: Dictionary with employee fields
        :return: Created EmployeeModel instance
        """
        return EmployeeModel.objects.create(
            department=department,
            full_name=employee_kwargs["full_name"],
            position=employee_kwargs["position"],
            hired_at=employee_kwargs.get("hired_at"),
        )
