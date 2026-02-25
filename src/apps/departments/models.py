"""Department database models."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DepartmentModel(models.Model):
    """Model representing an organizational department."""

    name = models.CharField(
        max_length=200,
        verbose_name=_("Name"),
        blank=False,
        null=False,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Parent"),
        related_name="children",
    )
    created_at = models.DateTimeField(_("Date of creation"), auto_now_add=True)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class EmployeeModel(models.Model):
    """Model representing an employee."""

    department = models.ForeignKey(
        DepartmentModel,
        on_delete=models.CASCADE,
        verbose_name=_("Department"),
        related_name="employees",
    )
    full_name = models.CharField(
        max_length=200, verbose_name=_("Full name"), blank=False, null=False
    )
    position = models.CharField(
        max_length=200, verbose_name=_("Position"), blank=False, null=False
    )
    hired_at = models.DateField(_("Hired date"), null=True, blank=True)
    created_at = models.DateTimeField(_("Date of creation"), auto_now_add=True)

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name
