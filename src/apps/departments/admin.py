from django.contrib import admin

from src.apps.departments.models import DepartmentModel, EmployeeModel


@admin.register(DepartmentModel)
class DepartmentModelAdmin(admin.ModelAdmin):
    """Admin configuration for DepartmentModel."""

    fields = ["name", "parent_id", "created_at"]
    list_display = [
        "id",
        "parent_id",
        "name",
    ]
    list_filter = [
        "parent_id",
        "name",
    ]
    readonly_fields = ["created_at"]


@admin.register(EmployeeModel)
class EmployeeModelAdmin(admin.ModelAdmin):
    """Admin configuration for EmployeeModel."""

    fields = ["department_id", "full_name", "position", "hired_at", "created_at"]
    list_display = [
        "id",
        "department_id",
        "full_name",
    ]
    list_filter = ["full_name", "position"]
    readonly_fields = ["created_at"]
