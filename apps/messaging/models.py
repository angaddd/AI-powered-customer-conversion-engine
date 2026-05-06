from django.db import models

from apps.companies.models import Company
from apps.leads.models import Lead


class MessageTemplate(models.Model):
    CHANNEL_CHOICES = [("email", "Email"), ("sms", "SMS")]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="message_templates")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    name = models.CharField(max_length=120)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    variables = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company", "name", "channel")


class MessageLog(models.Model):
    STATUS_CHOICES = [("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="message_logs")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, related_name="message_logs", null=True, blank=True)
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=180)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    provider_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["company", "created_at"]), models.Index(fields=["company", "channel"])]

