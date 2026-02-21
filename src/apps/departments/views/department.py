"""Department ViewSet for REST API endpoints."""

from http import HTTPMethod
from rest_framework import viewsets
from src.apps.departments.models import DepartmentModel
from src.apps.departments.serializers.department import DepartmentSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Department instances."""

    queryset = DepartmentModel.objects.all()
    serializer_class = DepartmentSerializer
    http_method_names = [
        HTTPMethod.GET.lower(),
        HTTPMethod.POST.lower(),
        HTTPMethod.PATCH.lower(),
        HTTPMethod.DELETE.lower(),
    ]
