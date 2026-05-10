from datetime import timedelta

from django.utils import timezone


def category_for_score(score, purchases=0):
    if purchases:
        return "customer"
    if score >= 70:
        return "hot_lead"
    if score >= 30:
        return "warm_lead"
    return "cold_visitor"


def score_lead(lead):
    score = 0
    score += min(lead.total_page_views, 20) * 1
    score += min(lead.total_product_views, 10) * 5
    score += lead.total_cart_adds * 20
    score += lead.total_checkout_attempts * 30
    score += lead.total_purchases * 100

    if lead.name:
        score += 5
    if lead.email:
        score += 15
    if lead.phone:
        score += 10
    if lead.total_sessions >= 2:
        score += 15
    if lead.total_cart_adds and not lead.total_purchases:
        score += 25
    if lead.last_seen_at and lead.last_seen_at < timezone.now() - timedelta(days=30):
        score -= 20

    score = max(0, min(score, 150))
    lead.intent_score = score
    lead.intent_category = category_for_score(score, lead.total_purchases)
    lead.save(update_fields=["intent_score", "intent_category", "updated_at"])
    return score
