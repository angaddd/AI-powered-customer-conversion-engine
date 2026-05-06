from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.ai_engine.models import AIInsight
from apps.automations.models import AutomationRule
from apps.companies.models import Company, CompanyMembership
from apps.events.services import ingest_event
from apps.messaging.models import MessageTemplate


class Command(BaseCommand):
    help = "Create demo tenant, admin user, templates, automations, and sample events."

    def handle(self, *args, **options):
        company, _ = Company.objects.get_or_create(
            public_key="pk_demo_store",
            defaults={"name": "Demo Commerce Co", "domain": "localhost:9000", "plan": "growth"},
        )
        user, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        user.set_password("admin12345")
        user.save()
        CompanyMembership.objects.get_or_create(company=company, user=user, defaults={"role": "owner"})

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

        now = timezone.now()
        demo_events = [
            ("visitor_demo_1", "session_demo_1", "page_view", {}),
            ("visitor_demo_1", "session_demo_1", "product_view", {"product_id": "consulting-plus", "value": 499}),
            ("visitor_demo_1", "session_demo_1", "add_to_cart", {"product_id": "consulting-plus", "value": 499}),
            ("visitor_demo_2", "session_demo_2", "page_view", {}),
            ("visitor_demo_2", "session_demo_2", "product_view", {"product_id": "starter-kit", "value": 99}),
            ("visitor_demo_3", "session_demo_3", "page_view", {}),
            ("visitor_demo_3", "session_demo_3", "checkout_started", {"value": 199}),
            ("visitor_demo_3", "session_demo_3", "purchase_completed", {"value": 199}),
        ]
        for visitor_id, session_id, event_type, properties in demo_events:
            ingest_event({
                "public_key": company.public_key,
                "visitor_id": visitor_id,
                "session_id": session_id,
                "event_type": event_type,
                "url": "http://localhost:9000/",
                "timestamp": now,
                "properties": properties,
                "identity": {
                    "email": f"{visitor_id}@example.com",
                    "phone": "+15555550123",
                    "name": visitor_id.replace("_", " ").title(),
                },
            })

        AIInsight.objects.get_or_create(
            company=company,
            insight_type="funnel_dropoff",
            title="Cart engagement is strong",
            defaults={
                "description": "Demo data shows visitors reaching the cart after product engagement.",
                "recommendation": "Send a short reminder with a small discount to recover abandoned carts.",
                "confidence_score": 0.82,
            },
        )
        self.stdout.write(self.style.SUCCESS("Demo tenant ready: admin@example.com / admin12345"))
