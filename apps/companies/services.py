import secrets

from django.contrib.auth.models import User

from apps.automations.models import AutomationRule
from apps.messaging.models import MessageTemplate
from .models import Company, CompanyMembership


def generate_public_key():
    while True:
        public_key = f"pk_live_{secrets.token_hex(16)}"
        if not Company.objects.filter(public_key=public_key).exists():
            return public_key


def provision_company_for_user(user: User, name=None, domain=""):
    company = Company.objects.create(
        name=name or f"{user.username}'s Company",
        domain=domain,
        allowed_origins=[domain] if domain else [],
        public_key=generate_public_key(),
        plan="starter",
    )
    CompanyMembership.objects.create(company=company, user=user, role="owner")
    ensure_company_defaults(company)
    return company


def ensure_company_defaults(company):
    MessageTemplate.objects.get_or_create(
        company=company,
        channel="email",
        name="cart_reminder",
        defaults={
            "subject": "Still thinking it over, {{ name }}?",
            "body": "Your cart is waiting. Complete your purchase today and use code SAVE10.",
            "variables": ["name"],
        },
    )
    MessageTemplate.objects.get_or_create(
        company=company,
        channel="sms",
        name="hot_lead_sms",
        defaults={
            "body": "Hi {{ name }}, thanks for browsing. Reply here if you need help choosing the right option.",
            "variables": ["name"],
        },
    )
    AutomationRule.objects.get_or_create(
        company=company,
        name="Cart reminder email",
        defaults={
            "trigger_type": "event_based",
            "conditions": {"event": "add_to_cart"},
            "actions": [{"type": "send_email", "template": "cart_reminder"}],
            "cooldown_minutes": 120,
        },
    )
    AutomationRule.objects.get_or_create(
        company=company,
        name="Hot lead SMS",
        defaults={
            "trigger_type": "score_based",
            "conditions": {"intent_score_greater_than": 70},
            "actions": [{"type": "send_sms", "template": "hot_lead_sms"}],
            "cooldown_minutes": 240,
        },
    )
