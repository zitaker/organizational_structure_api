"""Module for working with a database."""

from typing import TypeVar

from django.db import transaction
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound

from src.apps.departments.models import DepartmentModel

T = TypeVar("T", bound=Model)


class DepartmentDatabase:
    """Accessing the database."""

    model = DepartmentModel

    @staticmethod
    def delete_department_cascade(department: DepartmentModel) -> None:
        """
        Delete department with all its employees and child departments.
        :param department: Department to delete
        """
        department.delete()

    def get_target_department(self, reassign_to_id: str) -> DepartmentModel:
        """
        Get department by ID or raise NotFound exception.
        :param reassign_to_id: ID of target department for employee reassignment.
        :returns: DepartmentModel instance.
        :raises NotFound: If target department doesn't exist.
        """
        try:
            return self.model.objects.get(id=reassign_to_id)
        except self.model.DoesNotExist:
            raise NotFound(_("Target department not found."))

    @staticmethod
    def reassign_and_delete(
        department: DepartmentModel, target_department: DepartmentModel
    ) -> None:
        """
        Reassign all employees from department to target_department
        and delete the department.
        :param department: Department to delete.
        :param target_department: Department where employees will be reassigned.
        """
        with transaction.atomic():
            employees_manager = getattr(department, "employees")
            employees_manager.update(department=target_department)
            department.delete()

    def get_children(self, department: DepartmentModel) -> list[DepartmentModel]:
        """
        Get child departments as a list of model instances.
        :param department: Parent department instance.
        :return: List of child department instances (empty list if none).
        """
        return list(getattr(department, "children").all())

    def get_employees_count(self, department: DepartmentModel) -> int:
        """
        Get number of employees in department.
        :param department: Department instance.
        :return: Number of employees.
        """
        return getattr(department, "employees").count()

    def get_sorted_employees(self, department: DepartmentModel, sort_by: str) -> list:
        """
        Get sorted employees as list.
        :param department: Department instance.
        :param sort_by: Field to sort by ('full_name' or 'created_at').
        :return: List of employee instances.
        """
        qs = getattr(department, "employees").all()

        if sort_by == "full_name":
            qs = qs.order_by("full_name")
        else:
            qs = qs.order_by("created_at")

        return list(qs)
