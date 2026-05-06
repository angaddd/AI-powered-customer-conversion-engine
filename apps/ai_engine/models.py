from django.db import models

from apps.companies.models import Company


class AIInsight(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="ai_insights")
    insight_type = models.CharField(max_length=80)
    title = models.CharField(max_length=220)
    description = models.TextField()
    recommendation = models.TextField()
    confidence_score = models.FloatField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["company", "created_at"]), models.Index(fields=["company", "insight_type"])]

