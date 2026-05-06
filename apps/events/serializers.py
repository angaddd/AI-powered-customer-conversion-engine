from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["company", "lead", "visitor_session"]


class TrackEventSerializer(serializers.Serializer):
    public_key = serializers.CharField(max_length=80)
    visitor_id = serializers.CharField(max_length=120)
    session_id = serializers.CharField(max_length=120)
    event_type = serializers.CharField(max_length=40)
    url = serializers.URLField(required=False, allow_blank=True)
    timestamp = serializers.DateTimeField()
    properties = serializers.JSONField(required=False)
    identity = serializers.JSONField(required=False)
