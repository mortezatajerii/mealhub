from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Organization, Department
from .serializers import OrganizationSerializer, DepartmentSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.prefetch_related("departments").all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related("organization").all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = self.request.query_params.get("organization")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs
