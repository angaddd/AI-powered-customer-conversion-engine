from django.db import models

from apps.companies.models import Company
from apps.leads.models import Lead


class AutomationRule(models.Model):
    TRIGGER_CHOICES = [
        ("event_based", "Event Based"),
        ("score_based", "Score Based"),
        ("time_based", "Time Based"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="automation_rules")
    name = models.CharField(max_length=160)
    trigger_type = models.CharField(max_length=40, choices=TRIGGER_CHOICES)
    conditions = models.JSONField(default=dict, blank=True)
    actions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    cooldown_minutes = models.PositiveIntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["company", "trigger_type", "is_active"])]


class AutomationExecution(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="automation_executions")
    automation_rule = models.ForeignKey(AutomationRule, on_delete=models.CASCADE, related_name="executions")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="automation_executions")
    status = models.CharField(max_length=30, default="executed")
    trigger_event_id = models.PositiveIntegerField(null=True, blank=True)
    result = models.JSONField(default=dict, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["company", "executed_at"])]

