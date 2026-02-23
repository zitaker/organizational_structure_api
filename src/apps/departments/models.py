"""Department database models."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DepartmentModel(models.Model):
    """Model representing an organizational department."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    create_at = models.DateTimeField(_("Date of creation"), auto_now_add=True)

    def __str__(self):
        return self.name
