from django.contrib import admin

from src.apps.departments.models import DepartmentModel


@admin.register(DepartmentModel)
class DepartmentModelAdmin(admin.ModelAdmin):

    fields = ["__all__"]
    list_display = [
        "id",
        "name",
    ]
    list_filter = [
        "name",
    ]
