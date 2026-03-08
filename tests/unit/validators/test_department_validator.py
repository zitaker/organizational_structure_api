"""Module for DepartmentValidator tests."""

import re

import pytest
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
        expected_value = str(_("Can only contain letters and spaces."))
        expected_message = str(
            {
                "name": [
                    expected_value,
                ]
            }
        )
        with pytest.raises(
            ValidationError,
            match=re.escape(expected_message),
        ) as exc:
            self.validator._validate_name_format(name)
        assert "name" in exc.value.message_dict


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
        expected_value = str(_("Department with this name already."))
        expected_message = str(
            {
                "name": [
                    expected_value,
                ]
            }
        )
        with pytest.raises(
            ValidationError,
            match=re.escape(expected_message),
        ) as exc:
            self.validator._validate_unique_name_in_parent(
                name=existing_name, parent=parent, instance=None
            )
        assert "name" in exc.value.message_dict

    def test_validate_unique_name_in_parent_validation_error_instance(self):
        """
        Negative unit tests instance ValidationError
        for _validate_unique_name_in_parent.
        """
        parent = DepartmentFactory(name="Parent qwerty")
        existing_name = "qwerty"
        DepartmentFactory(name=existing_name, parent=parent)
        expected_value = str(_("Department with this name already."))
        expected_message = str(
            {
                "name": [
                    expected_value,
                ]
            }
        )
        with pytest.raises(
            ValidationError,
            match=re.escape(expected_message),
        ) as exc:
            self.validator._validate_unique_name_in_parent(
                name=existing_name,
                parent=parent,
                instance=DepartmentFactory(name="old_name", parent=parent),
            )
        assert "name" in exc.value.message_dict
