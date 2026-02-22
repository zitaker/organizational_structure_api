"""Departments app URL routing with DRF DefaultRouter."""

from rest_framework.routers import DefaultRouter

from src.apps.departments.views.department import DepartmentViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="departments")

urlpatterns = []
urlpatterns += router.urls
