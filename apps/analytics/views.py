from decimal import Decimal

from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework import decorators, permissions, response, viewsets

from apps.companies.tenant import get_user_company
from apps.events.models import Event
from apps.leads.models import Lead


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        return self.overview(request)

    @decorators.action(detail=False, methods=["get"])
    def overview(self, request):
        company = get_user_company(request.user)
        if not company:
            return response.Response({})
        events = Event.objects.filter(company=company)
        leads = Lead.objects.filter(company=company)
        purchases = events.filter(event_type="purchase_completed")
        revenue = sum(Decimal(str(event.properties.get("value", 0))) for event in purchases)
        visitors = leads.count()
        conversions = purchases.values("visitor_id").distinct().count()
        return response.Response({
            "total_visitors": visitors,
            "total_events": events.count(),
            "hot_leads": leads.filter(intent_category="hot_lead").count(),
            "abandoned_carts": leads.filter(total_cart_adds__gt=0, total_purchases=0).count(),
            "purchases": purchases.count(),
            "revenue": revenue,
            "conversion_rate": round((conversions / visitors) * 100, 2) if visitors else 0,
        })

    @decorators.action(detail=False, methods=["get"])
    def funnel(self, request):
        company = get_user_company(request.user)
        counts = Event.objects.filter(company=company).values("event_type").annotate(count=Count("id"))
        lookup = {item["event_type"]: item["count"] for item in counts}
        return response.Response([
            {"stage": "Page View", "count": lookup.get("page_view", 0)},
            {"stage": "Product View", "count": lookup.get("product_view", 0)},
            {"stage": "Add To Cart", "count": lookup.get("add_to_cart", 0)},
            {"stage": "Checkout", "count": lookup.get("checkout_started", 0)},
            {"stage": "Purchase", "count": lookup.get("purchase_completed", 0)},
        ])

    @decorators.action(detail=False, methods=["get"], url_path="revenue-trend")
    def revenue_trend(self, request):
        company = get_user_company(request.user)
        events = (
            Event.objects
            .filter(company=company, event_type="purchase_completed")
            .annotate(day=TruncDate("timestamp"))
            .order_by("day")
        )
        daily = {}
        for event in events:
            key = event.day.isoformat()
            daily.setdefault(key, {"date": key, "revenue": Decimal("0"), "purchases": 0})
            daily[key]["revenue"] += Decimal(str(event.properties.get("value", 0)))
            daily[key]["purchases"] += 1
        return response.Response([
            {"date": item["date"], "revenue": float(item["revenue"]), "purchases": item["purchases"]}
            for item in daily.values()
        ])

    @decorators.action(detail=False, methods=["get"], url_path="event-mix")
    def event_mix(self, request):
        company = get_user_company(request.user)
        counts = Event.objects.filter(company=company).values("event_type").annotate(count=Count("id")).order_by("event_type")
        return response.Response([
            {"name": item["event_type"].replace("_", " ").title(), "count": item["count"]}
            for item in counts
        ])
