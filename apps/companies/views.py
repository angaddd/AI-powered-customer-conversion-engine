from rest_framework import permissions, viewsets

from .models import Company
from .serializers import CompanySerializer
from .tenant import get_user_company


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        company = get_user_company(self.request.user)
        return Company.objects.filter(id=company.id) if company else Company.objects.none()
