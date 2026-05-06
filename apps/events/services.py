from urllib.parse import urlparse

from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models import F
from django.utils.dateparse import parse_datetime

from apps.ai_engine.tasks import generate_company_insights_task
from apps.ai_engine.scoring import score_lead
from apps.automations.services import evaluate_automations
from apps.companies.models import Company
from apps.leads.models import Lead, VisitorSession
from .models import Event


EVENT_COUNTERS = {
    "page_view": "total_page_views",
    "product_view": "total_product_views",
    "add_to_cart": "total_cart_adds",
    "checkout_started": "total_checkout_attempts",
    "purchase_completed": "total_purchases",
}


def _origin_host(value):
    """Extract host:port from various URL formats"""
    if not value:
        return ""
    value = value.strip()
    parsed = urlparse(value)
    # If urlparse found a netloc, use it
    if parsed.netloc:
        return parsed.netloc
    # If no scheme was provided, try parsing it as host:port directly
    if "://" not in value:
        return value
    # Fallback to path if neither worked
    return parsed.path


def get_tracking_company(payload, request=None):
    company = Company.objects.get(public_key=payload["public_key"], is_active=True)
    allowed = set(company.allowed_origins or [])
    if company.domain:
        allowed.add(company.domain)
    if not allowed:
        return company

    origin = request.headers.get("Origin", "") if request else ""
    referer = request.headers.get("Referer", "") if request else ""
    url = payload.get("url", "")
    
    # Extract candidate hosts
    candidate_hosts = {_origin_host(origin), _origin_host(referer), _origin_host(url)}
    candidate_hosts.discard("")  # Remove empty strings
    
    # Extract allowed hosts (don't parse them, use them as-is for comparison)
    allowed_hosts = {_origin_host(item) for item in allowed}
    allowed_hosts.discard("")  # Remove empty strings
    
    # If no candidates provided, allow it (public tracking allowed)
    if not candidate_hosts or not allowed_hosts:
        return company
    
    if candidate_hosts.isdisjoint(allowed_hosts):
        raise PermissionDenied("Tracking origin is not allowed for this company.")
    return company


def ingest_event(payload, request=None):
    company = get_tracking_company(payload, request=request)
    identity = payload.get("identity") or {}
    properties = payload.get("properties") or {}
    visitor_id = payload["visitor_id"]
    timestamp = payload["timestamp"]
    if isinstance(timestamp, str):
        timestamp = parse_datetime(timestamp)

    lead, created = Lead.objects.get_or_create(
        company=company,
        visitor_id=visitor_id,
        defaults={
            "email": identity.get("email", ""),
            "phone": identity.get("phone", ""),
            "name": identity.get("name", ""),
            "first_seen_at": timestamp,
            "last_seen_at": timestamp,
        },
    )
    updates = {"last_seen_at": timestamp}
    for field in ["email", "phone", "name"]:
        if identity.get(field):
            updates[field] = identity[field]
    Lead.objects.filter(id=lead.id).update(**updates)
    lead.refresh_from_db()

    session, session_created = VisitorSession.objects.get_or_create(
        company=company,
        session_id=payload["session_id"],
        defaults={
            "lead": lead,
            "visitor_id": visitor_id,
            "started_at": timestamp,
            "device": properties.get("device", ""),
            "browser": properties.get("browser", ""),
            "referrer": properties.get("referrer", ""),
            "utm_source": properties.get("utm_source", ""),
            "utm_campaign": properties.get("utm_campaign", ""),
        },
    )
    if session_created:
        Lead.objects.filter(id=lead.id).update(total_sessions=F("total_sessions") + 1)

    event = Event.objects.create(
        company=company,
        lead=lead,
        visitor_id=visitor_id,
        visitor_session=session,
        session_id=payload["session_id"],
        event_type=payload["event_type"],
        url=payload.get("url", ""),
        properties=properties,
        timestamp=timestamp,
    )

    counter = EVENT_COUNTERS.get(event.event_type)
    if counter:
        extra = {counter: F(counter) + 1}
        if event.event_type == "purchase_completed":
            extra["total_revenue"] = F("total_revenue") + properties.get("value", 0)
        Lead.objects.filter(id=lead.id).update(**extra)

    lead.refresh_from_db()
    score_lead(lead)
    evaluate_automations(event)
    try:
        cache.set(f"company:{company.id}:latest_event_id", event.id, timeout=3600)
    except Exception:
        pass
    try:
        generate_company_insights_task.delay(company.id)
    except Exception:
        pass
    return event
