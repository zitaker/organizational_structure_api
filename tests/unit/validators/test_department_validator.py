"""Module for DepartmentValidator tests."""

import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from src.apps.departments.validators import DepartmentValidator
from tests.factories import DepartmentFactory


class TestDepartmentValidatorBase:
    """A basic test class that provides calls in one place."""

    @property
    def validator(self):
        """DepartmentValidator instance for testing."""
        return DepartmentValidator()


@pytest.mark.django_db
class TestValidateNameFormat(TestDepartmentValidatorBase):
    """Unit tests for DepartmentValidator._validate_name_format."""

    def test_validate_name_format_positive(self):
        """Positive unit tests for _validate_name_format."""
        result = self.validator._validate_name_format("qwerty")
        assert result is None

    @pytest.mark.parametrize(
        "name",
        ["123", "@#$", "qwerty!1"],
    )
    def test_validate_name_format_validation_error(self, name):
        """
        Negative unit tests ValidationError for _validate_name_format.
        """
        with pytest.raises(ValidationError) as exc_info:
            self.validator._validate_name_format(name)
        error = exc_info.value
        assert error.detail == {"name": _("Can only contain letters and spaces.")}
        assert error.detail["name"].code == "invalid"
        assert error.status_code == 400


@pytest.mark.django_db
class TestValidateUniqueNameInParent(TestDepartmentValidatorBase):
    """Unit tests for DepartmentValidator._validate_unique_name_in_parent."""

    def test_validate_unique_name_in_parent_positive(self):
        """Positive unit tests for _validate_unique_name_in_parent."""
        result = self.validator._validate_unique_name_in_parent(
            name="qwerty", parent=DepartmentFactory(name="Parent qwerty"), instance=None
        )
        assert result is None

    def test_validate_unique_name_in_parent_positive_instance(self):
        """Positive unit tests instance for _validate_unique_name_in_parent."""
        name = "qwerty"
        parent = DepartmentFactory(name="Parent qwerty")
        instance = DepartmentFactory(name=name, parent=parent)
        result = self.validator._validate_unique_name_in_parent(
            name=name, parent=parent, instance=instance
        )
        assert result is None

    def test_validate_unique_name_in_parent_validation_error(self):
        """
        Negative unit tests ValidationError for _validate_unique_name_in_parent.
        """
        parent = DepartmentFactory(name="qwerty123")
        existing_name = "qwerty"
        DepartmentFactory(name=existing_name, parent=parent)
        with pytest.raises(ValidationError) as exc_info:
            self.validator._validate_unique_name_in_parent(
                name=existing_name, parent=parent, instance=None
            )
        error = exc_info.value
        assert error.detail == {"name": _("Department with this name already.")}
        assert error.status_code == 400
        assert error.detail["name"].code == "invalid"

    def test_validate_unique_name_in_parent_validation_error_instance(self):
        """
        Negative unit tests instance ValidationError
        for _validate_unique_name_in_parent.
        """
        parent = DepartmentFactory(name="Parent qwerty")
        existing_name = "qwerty"
        DepartmentFactory(name=existing_name, parent=parent)
        with pytest.raises(ValidationError) as exc_info:
            self.validator._validate_unique_name_in_parent(
                name=existing_name,
                parent=parent,
                instance=DepartmentFactory(name="old_name", parent=parent),
            )
        error = exc_info.value
        assert error.detail == {"name": _("Department with this name already.")}
        assert error.status_code == 400
        assert error.detail["name"].code == "invalid"
