from django.contrib import admin

from src.apps.departments.models import DepartmentModel, EmployeeModel


@admin.register(DepartmentModel)
class DepartmentModelAdmin(admin.ModelAdmin):
    """Admin configuration for DepartmentModel."""

    fields = ["name", "parent", "created_at"]
    list_display = [
        "id",
        "parent",
        "name",
    ]
    list_filter = [
        "parent",
        "name",
    ]
    readonly_fields = ["created_at"]


@admin.register(EmployeeModel)
class EmployeeModelAdmin(admin.ModelAdmin):
    """Admin configuration for EmployeeModel."""

    fields = ["department", "full_name", "position", "hired_at", "created_at"]
    list_display = [
        "id",
        "department",
        "full_name",
    ]
    list_filter = ["full_name", "position"]
    readonly_fields = ["created_at"]
