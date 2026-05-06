from django.db import models

from apps.companies.models import Company


class DailyCompanyMetric(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="daily_metrics")
    date = models.DateField()
    total_visitors = models.PositiveIntegerField(default=0)
    total_events = models.PositiveIntegerField(default=0)
    hot_leads = models.PositiveIntegerField(default=0)
    abandoned_carts = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "date")

