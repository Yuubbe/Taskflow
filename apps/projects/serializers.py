"""Project serializers."""

from typing import Any

from rest_framework import serializers

from apps.projects.models import Project, ProjectMembership
from apps.users.serializers import UserSerializer


class ProjectMembershipSerializer(serializers.ModelSerializer[ProjectMembership]):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ["id", "user", "role", "joined_at"]


class ProjectSerializer(serializers.ModelSerializer[Project]):
    owner = UserSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "name", "description", "status", "owner", "member_count", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_member_count(self, obj: Project) -> int:
        return obj.memberships.count()

    def create(self, validated_data: dict[str, Any]) -> Project:
        request = self.context["request"]
        project: Project = Project.objects.create(owner=request.user, **validated_data)
        # Owner is automatically a member with admin role
        ProjectMembership.objects.create(user=request.user, project=project, role=ProjectMembership.Role.ADMIN)
        return project


class AddMemberSerializer(serializers.Serializer[Any]):
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=ProjectMembership.Role.choices, default=ProjectMembership.Role.CONTRIBUTOR)
