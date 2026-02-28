"""Service for Employee business logic."""

from src.apps.departments.models import DepartmentModel, EmployeeModel


class EmployeeService:
    """Service class for Employee operations."""

    model = EmployeeModel

    def create_employee(
        self, department: DepartmentModel, **employee_kwargs
    ) -> EmployeeModel:
        """
        Create a new employee.
        :param department: Department instance
        :param employee_kwargs: Dictionary with employee fields
        :return: Created EmployeeModel instance
        """
        return self.model.objects.create(
            department=department,
            full_name=employee_kwargs["full_name"],
            position=employee_kwargs["position"],
            hired_at=employee_kwargs.get("hired_at"),
        )
