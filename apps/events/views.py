from django.conf import settings
from django.http import HttpResponse
from rest_framework import permissions, response, status, views, viewsets

from apps.companies.tenant import TenantScopedMixin
from apps.companies.models import Company
from .models import Event
from .serializers import EventSerializer, TrackEventSerializer
from .services import ingest_event
from .tasks import ingest_event_task


class TrackingScriptView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request, public_key):
        Company.objects.get(public_key=public_key, is_active=True)
        endpoint = request.build_absolute_uri("/api/events/track/")
        script = f"""
(function () {{
  window.ConversionEngineConfig = Object.assign({{}}, window.ConversionEngineConfig || {{}}, {{
    publicKey: "{public_key}",
    endpoint: "{endpoint}"
  }});
}})();
"""
        try:
            from pathlib import Path
            sdk_path = Path(__file__).resolve().parents[3] / "sdk" / "tracker.js"
            script += sdk_path.read_text(encoding="utf-8")
        except Exception:
            script += """
(function () {
  const config = window.ConversionEngineConfig || {};
  const endpoint = config.endpoint;
  const publicKey = config.publicKey;
  function uuid(prefix) {
    return prefix + "_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  }
  function getStored(key, fallback) {
    try {
      const existing = localStorage.getItem(key);
      if (existing) return existing;
      localStorage.setItem(key, fallback);
      return fallback;
    } catch (error) {
      return fallback;
    }
  }
  const visitorId = getStored("ce_visitor_id", uuid("visitor"));
  const sessionId = getStored("ce_session_id", uuid("session"));
  let identity = {};
  function baseProperties() {
    return {
      title: document.title,
      referrer: document.referrer,
      device: /Mobi|Android/i.test(navigator.userAgent) ? "mobile" : "desktop",
      browser: navigator.userAgent,
      utm_source: new URLSearchParams(location.search).get("utm_source") || "",
      utm_campaign: new URLSearchParams(location.search).get("utm_campaign") || ""
    };
  }
  function track(eventType, properties) {
    const body = JSON.stringify({
      public_key: publicKey,
      visitor_id: visitorId,
      session_id: sessionId,
      event_type: eventType,
      url: location.href,
      timestamp: new Date().toISOString(),
      properties: Object.assign(baseProperties(), properties || {}),
      identity: identity
    });
    if (navigator.sendBeacon) {
      try {
        if (navigator.sendBeacon(endpoint, new Blob([body], { type: "application/json" }))) {
          return Promise.resolve({ ok: true, beacon: true });
        }
      } catch (error) {}
    }
    return fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body,
      keepalive: true
    }).catch(function (error) {
      console.warn("ConversionEngine tracking failed", error);
    });
  }
  function identify(data) {
    identity = Object.assign(identity, data || {});
    return track("custom", { custom_event: "identify" });
  }
  window.ce = { track: track, identify: identify, visitorId: visitorId, sessionId: sessionId };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { track("page_view"); });
  } else {
    track("page_view");
  }
})();
"""
        return HttpResponse(script, content_type="application/javascript")


class EventTrackView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TrackEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        if not settings.TRACK_EVENTS_ASYNC:
            event = ingest_event(payload, request=request)
            return response.Response({"ok": True,
                                      "queued": False,
                                      "event_id": event.id},
                                     status=status.HTTP_201_CREATED)

        task_payload = dict(payload)
        task_payload["timestamp"] = task_payload["timestamp"].isoformat()
        try:
            async_result = ingest_event_task.delay(task_payload)
            return response.Response({"ok": True,
                                       "queued": True,
                                       "task_id": async_result.id},
                                       status=status.HTTP_202_ACCEPTED) #ignored response 
        except Exception:
            event = ingest_event(payload, request=request)
            return response.Response({"ok": True, 
                                      "queued": False, 
                                      "event_id": event.id}, 
                                      status=status.HTTP_201_CREATED)


class EventViewSet(TenantScopedMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.select_related("lead").all().order_by("-timestamp")
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
