from rest_framework import decorators, permissions, response, status, viewsets

from apps.companies.tenant import TenantScopedMixin
from apps.leads.models import Lead
from .services import send_message
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

    @decorators.action(detail=False, methods=["post"], url_path="send-hot-sms")
    def send_hot_sms(self, request):
        company = self.get_company()
        if not company:
            return response.Response({"detail": "No company is attached to this user."}, status=status.HTTP_400_BAD_REQUEST)

        leads = Lead.objects.filter(
            company=company,
            intent_category__in=["hot_lead", "customer"],
        ).exclude(phone="")

        sent = []
        failed = []
        for lead in leads:
            try:
                log = send_message(company, lead, "sms", "hot_lead_sms", {"event_type": "manual_hot_lead_blast"})
                if log:
                    sent.append(log.id)
            except Exception as exc:
                failed.append({"lead_id": lead.id, "error": str(exc)})

        skipped = Lead.objects.filter(
            company=company,
            intent_category__in=["hot_lead", "customer"],
            phone="",
        ).count()
        return response.Response({
            "sent": len(sent),
            "message_log_ids": sent,
            "skipped_without_phone": skipped,
            "failed": failed,
        })
