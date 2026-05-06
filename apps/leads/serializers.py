from rest_framework import serializers

from .models import Lead, VisitorSession


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = ["company"]


class VisitorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorSession
        fields = "__all__"
        read_only_fields = ["company"]

