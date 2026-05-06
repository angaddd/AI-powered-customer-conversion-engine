from rest_framework import permissions, response, status, views, viewsets

from apps.companies.tenant import TenantScopedMixin
from .models import Event
from .serializers import EventSerializer, TrackEventSerializer
from .services import ingest_event
from .tasks import ingest_event_task


class EventTrackView(views.APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TrackEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
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
