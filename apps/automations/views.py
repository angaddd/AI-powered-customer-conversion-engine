from rest_framework import decorators, permissions, response, viewsets

from apps.companies.tenant import TenantScopedMixin
from .models import AutomationRule
from .serializers import AutomationExecutionSerializer, AutomationRuleSerializer


class AutomationRuleViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = AutomationRule.objects.all().order_by("-created_at")
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=True, methods=["get"])
    def executions(self, request, pk=None):
        rule = self.get_object()
        return response.Response(AutomationExecutionSerializer(rule.executions.order_by("-executed_at")[:100], many=True).data)

