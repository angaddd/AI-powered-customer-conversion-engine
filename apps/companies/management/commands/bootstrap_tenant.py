from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.automations.models import AutomationRule
from apps.companies.models import Company, CompanyMembership
from apps.messaging.models import MessageTemplate


class Command(BaseCommand):
    help = "Create a real tenant, dashboard user, message templates, and automations without fake visitor/event data."

    def add_arguments(self, parser):
        parser.add_argument("--company", default="Northstar Studio")
        parser.add_argument("--domain", default="127.0.0.1:9000")
        parser.add_argument("--public-key", default="pk_live_local")
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@example.com")
        parser.add_argument("--password", default="admin12345")

    def handle(self, *args, **options):
        company, _ = Company.objects.get_or_create(
            public_key=options["public_key"],
            defaults={
                "name": options["company"],
                "domain": options["domain"],
                "allowed_origins": [options["domain"], "localhost:9000", "127.0.0.1:9000"],
                "plan": "growth",
            },
        )
        company.name = options["company"]
        company.domain = options["domain"]
        company.allowed_origins = list(set(company.allowed_origins + [options["domain"], "localhost:9000", "127.0.0.1:9000"]))
        company.save()

        user, _ = User.objects.get_or_create(username=options["username"], defaults={"email": options["email"]})
        user.email = options["email"]
        user.set_password(options["password"])
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

        self.stdout.write(self.style.SUCCESS(
            f"Tenant ready without dummy events. Login: {options['username']} / {options['password']}. Public key: {company.public_key}"
        ))
