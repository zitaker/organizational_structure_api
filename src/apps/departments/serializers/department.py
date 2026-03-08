"""Serializer for DepartmentModel."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from src.apps.departments.models import DepartmentModel


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for DepartmentModel with all fields."""

    name = serializers.CharField(
        label=_("Name"),
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    parent = serializers.PrimaryKeyRelatedField(
        label=_("Parent id"),
        queryset=DepartmentModel.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DepartmentModel
        fields = ["id", "name", "parent", "created_at"]
