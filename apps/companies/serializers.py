from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "domain", "allowed_origins", "public_key", "plan", "is_active", "settings", "created_at"]
        read_only_fields = ["public_key", "created_at"]
