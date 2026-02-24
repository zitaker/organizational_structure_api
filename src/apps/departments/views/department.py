"""DepartmentViewSet for REST API endpoints."""

from http import HTTPMethod

from django.http import Http404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.departments.models import DepartmentModel
from src.apps.departments.serializers.department import DepartmentSerializer
from src.apps.departments.serializers.department_tree import DepartmentTreeSerializer


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
                    "Depth: 0-none, 1-direct, 2-levels. No depth = full tree."
                ),
                required=False,
            ),
        ],
        responses={status.HTTP_200_OK: DepartmentTreeSerializer},
    )
    def retrieve(self, request: Request, *args: tuple, **kwargs: dict[str, str]):
        """Retrieve a department instance with its tree structure."""
        try:
            instance = self.get_object()
        except Http404:
            raise NotFound(_("Department not found."))

        serializer = DepartmentTreeSerializer(instance, context={"request": request})
        return Response(serializer.data)
