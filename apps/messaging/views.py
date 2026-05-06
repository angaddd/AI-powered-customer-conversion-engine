from rest_framework import permissions, viewsets

from apps.companies.tenant import TenantScopedMixin
from .models import MessageLog, MessageTemplate
from .serializers import MessageLogSerializer, MessageTemplateSerializer


class MessageTemplateViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all().order_by("name")
    serializer_class = MessageTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class MessageLogViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = MessageLog.objects.all().order_by("-created_at")
    serializer_class = MessageLogSerializer
    permission_classes = [permissions.IsAuthenticated]
