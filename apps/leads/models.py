from django.db import models

from apps.companies.models import Company


class Lead(models.Model):
    INTENT_CHOICES = [
        ("cold_visitor", "Cold Visitor"),
        ("warm_lead", "Warm Lead"),
        ("hot_lead", "Hot Lead"),
        ("customer", "Customer"),
        ("at_risk_customer", "At Risk Customer"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="leads")
    visitor_id = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=40, default="new")
    intent_score = models.IntegerField(default=0)
    intent_category = models.CharField(max_length=40, choices=INTENT_CHOICES, default="cold_visitor")
    first_seen_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)
    total_page_views = models.PositiveIntegerField(default=0)
    total_product_views = models.PositiveIntegerField(default=0)
    total_cart_adds = models.PositiveIntegerField(default=0)
    total_checkout_attempts = models.PositiveIntegerField(default=0)
    total_purchases = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company", "visitor_id")
        indexes = [
            models.Index(fields=["company", "visitor_id"]),
            models.Index(fields=["company", "intent_category"]),
            models.Index(fields=["company", "intent_score"]),
        ]

    def __str__(self):
        return self.email or self.visitor_id


class VisitorSession(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="visitor_sessions")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="sessions", null=True, blank=True)
    visitor_id = models.CharField(max_length=120)
    session_id = models.CharField(max_length=120)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    device = models.CharField(max_length=80, blank=True)
    browser = models.CharField(max_length=80, blank=True)
    referrer = models.URLField(blank=True)
    utm_source = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "session_id")
        indexes = [models.Index(fields=["company", "visitor_id"]), models.Index(fields=["company", "session_id"])]

