from rest_framework import decorators, permissions, response, viewsets

from apps.companies.tenant import TenantScopedMixin
from apps.events.serializers import EventSerializer
from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-last_seen_at")
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"])
    def hot(self, request):
        queryset = self.get_queryset().filter(intent_category__in=["hot_lead", "customer"]).order_by("-intent_score")[:50]
        return response.Response(self.get_serializer(queryset, many=True).data)

    @decorators.action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        lead = self.get_object()
        events = lead.events.order_by("-timestamp")[:100]
        return response.Response(EventSerializer(events, many=True).data)
