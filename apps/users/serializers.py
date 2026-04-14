"""User serializers."""

from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    """Read serializer for User."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "avatar_url", "created_at"]
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.ModelSerializer[User]):
    """Registration serializer – creates a new user."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        return User.objects.create_user(**validated_data)


class UpdateProfileSerializer(serializers.ModelSerializer[User]):
    """Partial update for authenticated user's profile."""

    class Meta:
        model = User
        fields = ["username", "bio", "avatar_url"]
