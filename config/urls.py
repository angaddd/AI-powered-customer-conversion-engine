from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.analytics.views import AnalyticsViewSet
from apps.automations.views import AutomationRuleViewSet
from apps.companies.views import CompanyViewSet
from apps.events.views import EventTrackView, EventViewSet
from apps.leads.views import LeadViewSet
from apps.messaging.views import MessageTemplateViewSet, MessageLogViewSet
from apps.ai_engine.views import AIInsightViewSet

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="company")
router.register("leads", LeadViewSet, basename="lead")
router.register("events", EventViewSet, basename="event")
router.register("automations", AutomationRuleViewSet, basename="automation")
router.register("analytics", AnalyticsViewSet, basename="analytics")
router.register("message-templates", MessageTemplateViewSet, basename="message-template")
router.register("message-logs", MessageLogViewSet, basename="message-log")
router.register("ai-insights", AIInsightViewSet, basename="ai-insight")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/events/track/", EventTrackView.as_view(), name="event-track"),
    path("api/", include(router.urls)),
]
