from django.conf import settings
from django.db import models


class Company(models.Model):
    PLAN_CHOICES = [
        ("starter", "Starter"),
        ("growth", "Growth"),
        ("scale", "Scale"),
    ]

    name = models.CharField(max_length=180)
    domain = models.CharField(max_length=255, blank=True)
    allowed_origins = models.JSONField(default=list, blank=True)
    public_key = models.CharField(max_length=80, unique=True)
    plan = models.CharField(max_length=30, choices=PLAN_CHOICES, default="starter")
    is_active = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CompanyMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("marketer", "Marketer"),
        ("sales", "Sales"),
        ("analyst", "Analyst"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_memberships")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "user")
