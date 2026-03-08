"""Department database models."""

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class DepartmentModel(models.Model):
    """Model representing an organizational department."""

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
        help_text=_("Department name"),
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(2, message=_("Name must be at least 2 character long.")),
            MaxLengthValidator(
                200, message=_("Name must be no more than 200 characters long.")
            ),
        ],
        error_messages={
            "blank": _("Name cannot be empty."),
            "required": _("Name is required."),
            "null": _("Name cannot be null."),
        },
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Parent"),
        help_text=_("Parent department ID"),
        related_name="children",
        error_messages={
            "does_not_exist": _("Parent department with id {pk_value} does not exist."),
            "invalid": _("Incorrect type. Expected department ID value."),
        },
    )
    created_at = models.DateTimeField(_("Date of creation"), auto_now_add=True)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def clean(self):
        """Custom validation for department model."""
        from src.apps.departments.validators import DepartmentValidator

        validator = DepartmentValidator()
        validator.validate_department_data(
            name=self.name, parent=self.parent, instance=self
        )


class EmployeeModel(models.Model):
    """Model representing an employee."""

    department = models.ForeignKey(
        DepartmentModel,
        on_delete=models.CASCADE,
        verbose_name=_("Department"),
        help_text=_("Department where employee works"),
        related_name="employees",
        error_messages={
            "does_not_exist": _("Department with id {pk_value} does not exist."),
            "required": _("Department is required."),
        },
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name=_("Full name"),
        help_text=_("Employee full name"),
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(
                2, message=_("Full name must be at least 2 characters long.")
            ),
            MaxLengthValidator(
                200, message=_("Full name must be no more than 200 characters long.")
            ),
        ],
        error_messages={
            "blank": _("Full name cannot be empty."),
            "required": _("Full name is required."),
            "full_name": _("Full name cannot be null."),
        },
    )
    position = models.CharField(
        max_length=200,
        verbose_name=_("Position"),
        help_text=_("Employee position"),
        blank=False,
        null=False,
        validators=[
            MinLengthValidator(
                2, message=_("Position must be at least 2 characters long.")
            ),
            MaxLengthValidator(
                200, message=_("Position must be no more than 200 characters long.")
            ),
        ],
        error_messages={
            "blank": _("Position cannot be empty."),
            "required": _("Position is required."),
            "null": _("Position cannot be null."),
        },
    )
    hired_at = models.DateField(_("Hired date"), null=True, blank=True)
    created_at = models.DateTimeField(_("Date of creation"), auto_now_add=True)

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name

    def clean(self):
        """Custom validation for employee model."""
        from src.apps.departments.validators import EmployeeValidator

        validator = EmployeeValidator()
        validator.validate_employee_data(
            position=self.position,
            full_name=self.full_name,
            hired_at=self.hired_at,
        )
