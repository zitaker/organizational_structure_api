"""Employee ViewSet for REST API endpoints."""

from http import HTTPMethod

from rest_framework import viewsets

from src.apps.departments.models import EmployeeModel
from src.apps.departments.serializers.employee import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Employee instances."""

    queryset = EmployeeModel.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = [
        HTTPMethod.GET.lower(),
    ]
