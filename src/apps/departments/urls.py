"""Departments app URL routing with DRF DefaultRouter."""

from rest_framework.routers import DefaultRouter

from src.apps.departments.views.department import DepartmentViewSet
from src.apps.departments.views.employee import EmployeeViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="departments")
router.register("employees", EmployeeViewSet, basename="employees")

urlpatterns = []
urlpatterns += router.urls
