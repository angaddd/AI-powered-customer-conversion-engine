from decimal import Decimal

from django.db.models import Count

from apps.events.models import Event
from apps.leads.models import Lead
from .models import AIInsight


def generate_company_insights(company):
    events = Event.objects.filter(company=company)
    leads = Lead.objects.filter(company=company)
    if events.count() < 5:
        return []

    created = []
    abandoned = leads.filter(total_cart_adds__gt=0, total_purchases=0).count()
    hot_leads = leads.filter(intent_category="hot_lead").count()
    product_views = events.filter(event_type="product_view").count()
    cart_adds = events.filter(event_type="add_to_cart").count()
    purchases = events.filter(event_type="purchase_completed")
    revenue = sum(Decimal(str(event.properties.get("value", 0))) for event in purchases)

    if abandoned:
        insight, _ = AIInsight.objects.update_or_create(
            company=company,
            insight_type="cart_abandonment",
            defaults={
                "title": "Abandoned carts detected",
                "description": f"{abandoned} visitors added items to cart but have not purchased.",
                "recommendation": "Keep the cart reminder email active and test a small time-limited discount.",
                "confidence_score": 0.78,
                "metadata": {"abandoned_carts": abandoned},
            },
        )
        created.append(insight)

    if product_views and cart_adds / product_views < 0.2:
        insight, _ = AIInsight.objects.update_or_create(
            company=company,
            insight_type="product_dropoff",
            defaults={
                "title": "Product-to-cart drop-off is high",
                "description": "Many visitors view products but do not add them to cart.",
                "recommendation": "Improve offer clarity near pricing and add stronger proof close to product CTAs.",
                "confidence_score": 0.72,
                "metadata": {"product_views": product_views, "cart_adds": cart_adds},
            },
        )
        created.append(insight)

    if hot_leads:
        insight, _ = AIInsight.objects.update_or_create(
            company=company,
            insight_type="high_intent_buyers",
            defaults={
                "title": "High-intent buyers are active",
                "description": f"{hot_leads} leads currently have hot intent scores.",
                "recommendation": "Prioritize these leads for email or SMS follow-up before intent cools.",
                "confidence_score": 0.84,
                "metadata": {"hot_leads": hot_leads},
            },
        )
        created.append(insight)

    if revenue:
        top = (
            purchases
            .values("properties__product_id")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        if top and top["properties__product_id"]:
            insight, _ = AIInsight.objects.update_or_create(
                company=company,
                insight_type="revenue_product",
                defaults={
                    "title": "Revenue product signal found",
                    "description": f"{top['properties__product_id']} is appearing in purchase events.",
                    "recommendation": "Use this product as a featured offer in follow-up campaigns.",
                    "confidence_score": 0.7,
                    "metadata": {"product_id": top["properties__product_id"], "revenue": float(revenue)},
                },
            )
            created.append(insight)

    return created
