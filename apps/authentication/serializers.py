from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from apps.companies.services import provision_company_for_user


class RegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=180, required=False, allow_blank=True, write_only=True)
    domain = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("username", "email", "company_name", "domain", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return value

    def create(self, validated_data):
        company_name = validated_data.pop("company_name", "")
        domain = validated_data.pop("domain", "")
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        provision_company_for_user(user, name=company_name, domain=domain)
        return user
