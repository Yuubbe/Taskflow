"""Task serializers."""

from typing import Any

from rest_framework import serializers

from apps.tasks.models import Comment, Task
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer[Comment]):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "body", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def create(self, validated_data: dict[str, Any]) -> Comment:
        validated_data["author"] = self.context["request"].user
        validated_data["task_id"] = self.context["task_id"]
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer[Task]):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "project",
            "assignee",
            "assignee_id",
            "created_by",
            "due_date",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "project", "created_by", "created_at", "updated_at"]

    def get_comment_count(self, obj: Task) -> int:
        return obj.comments.count()


class TaskListSerializer(serializers.ModelSerializer[Task]):
    """Lightweight serializer for list views."""

    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "status", "priority", "assignee", "due_date", "created_at"]
