"""DepartmentViewSet for REST API endpoints."""

from http import HTTPMethod
from typing import Optional

from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.departments.models import DepartmentModel, EmployeeModel
from src.apps.departments.serializers.department import DepartmentSerializer
from src.apps.departments.serializers.department_retrieve import (
    DepartmentRetrieveSerializer,
)
from src.apps.departments.serializers.employee import (
    EmployeeCreateSerializer,
    EmployeeSerializer,
)
from src.apps.departments.services.employee import EmployeeService


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
    service = EmployeeService()

    @extend_schema(
        description=_("Retrieves a department with its tree structure."),
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description=_("A unique integer identifying the department."),
            ),
            OpenApiParameter(
                name="depth",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description=_(
                    "Depth of nested departments (default: 1, max: 5). "
                    "0 - no children, 1 - direct children only, etc."
                ),
                required=False,
            ),
            OpenApiParameter(
                name="include_employees",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=_(
                    "Whether to include employees in response (default: true). "
                    "Use 'false' to exclude employees."
                ),
                required=False,
                enum=["true", "false"],
            ),
            OpenApiParameter(
                name="sort_employees_by",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=_(
                    "Sort employees by field (default: created_at). "
                    "Available options: created_at, full_name"
                ),
                required=False,
                enum=["created_at", "full_name"],
            ),
        ],
        responses={status.HTTP_200_OK: DepartmentRetrieveSerializer},
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict[str, str]):
        """Retrieve a department instance with its tree structure."""
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound(_("Department not found."))

        serializer = DepartmentRetrieveSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        description=_("Create an employee in the specified department."),
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description=_("A unique integer identifying the department."),
            ),
        ],
        request=EmployeeCreateSerializer,
        responses={status.HTTP_201_CREATED: EmployeeSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="employees",
        serializer_class=EmployeeCreateSerializer,
    )
    def create_employee(self, request: Request, pk: Optional[int] = None):
        """Create an employee in the specified department."""
        department: DepartmentModel = self.get_object()
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        employee: EmployeeModel = self.service.create_employee(
            department=department, **create_serializer.validated_data
        )
        response_serializer = EmployeeSerializer(employee)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
