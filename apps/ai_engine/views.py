from rest_framework import permissions, viewsets

from apps.companies.tenant import TenantScopedMixin
from .models import AIInsight
from .serializers import AIInsightSerializer


class AIInsightViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AIInsight.objects.all().order_by("-created_at")
    serializer_class = AIInsightSerializer
    permission_classes = [permissions.IsAuthenticated]

