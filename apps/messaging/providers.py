from django.utils import timezone

from .models import MessageLog


class DevelopmentEmailProvider:
    def send(self, log: MessageLog):
        print(f"[email] to={log.recipient} subject={log.subject} body={log.body}")
        log.status = "sent"
        log.sent_at = timezone.now()
        log.provider_response = {"provider": "development_email", "delivered": True}
        log.save(update_fields=["status", "sent_at", "provider_response"])


class DevelopmentSMSProvider:
    def send(self, log: MessageLog):
        print(f"[sms] to={log.recipient} body={log.body}")
        log.status = "sent"
        log.sent_at = timezone.now()
        log.provider_response = {"provider": "development_sms", "delivered": True}
        log.save(update_fields=["status", "sent_at", "provider_response"])


def provider_for(channel):
    if channel == "sms":
        return DevelopmentSMSProvider()
    return DevelopmentEmailProvider()

