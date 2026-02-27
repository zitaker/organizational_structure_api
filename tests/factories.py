"""Factory classes for creating testing instances."""

from django.utils import timezone
from factory import Faker, LazyFunction, Sequence, SubFactory
from factory.django import DjangoModelFactory

from src.apps.departments.models import DepartmentModel, EmployeeModel


class DepartmentFactory(DjangoModelFactory):
    """Factory for creating DepartmentModel instances for testing."""

    class Meta:
        model = DepartmentModel

    name = Sequence(lambda n: f"Department {n}")
    parent = None
    created_at = LazyFunction(timezone.now)


class EmployeeFactory(DjangoModelFactory):
    """Factory for creating EmployeeModel instances for testing."""

    class Meta:
        model = EmployeeModel

    department = SubFactory(DepartmentFactory)
    full_name = Faker("name")
    position = Faker("job")
    hired_at = Faker("date_this_decade")
    created_at = LazyFunction(timezone.now)
