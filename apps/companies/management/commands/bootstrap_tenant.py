from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.companies.models import Company, CompanyMembership
from apps.companies.services import ensure_company_defaults


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

        ensure_company_defaults(company)

        self.stdout.write(self.style.SUCCESS(
            f"Tenant ready without dummy events. Login: {options['username']} / {options['password']}. Public key: {company.public_key}"
        ))
