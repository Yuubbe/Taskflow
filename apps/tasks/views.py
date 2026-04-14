"""Task views."""

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.models import Project
from apps.tasks.filters import TaskFilter
from apps.tasks.models import Comment, Task
from apps.tasks.serializers import CommentSerializer, TaskListSerializer, TaskSerializer


def _get_project_for_member(project_pk: int, request: Request) -> Project:
    """Return the project if the current user is a member, else raise 403."""
    project = get_object_or_404(Project, pk=project_pk)
    if not project.memberships.filter(user=request.user).exists():
        raise PermissionDenied("You are not a member of this project.")
    return project


class TaskListCreateView(generics.ListCreateAPIView[Task]):
    """
    GET  /api/projects/<project_pk>/tasks/  – list tasks (filterable).
    POST /api/projects/<project_pk>/tasks/  – create a task.
    """

    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority", "status"]

    def get_serializer_class(self):  # type: ignore[override]
        if self.request.method == "GET":
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self) -> QuerySet[Task]:
        # Enforces membership check for both GET and POST
        _get_project_for_member(self.kwargs["project_pk"], self.request)
        return Task.objects.filter(project_id=self.kwargs["project_pk"]).select_related("assignee", "created_by")

    def perform_create(self, serializer: TaskSerializer) -> None:  # type: ignore[override]
        project = _get_project_for_member(self.kwargs["project_pk"], self.request)
        serializer.save(project=project, created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView[Task]):
    """
    GET    /api/projects/<project_pk>/tasks/<pk>/
    PATCH  /api/projects/<project_pk>/tasks/<pk>/
    DELETE /api/projects/<project_pk>/tasks/<pk>/
    """

    serializer_class = TaskSerializer

    def get_queryset(self) -> QuerySet[Task]:
        return Task.objects.filter(project_id=self.kwargs["project_pk"]).select_related(
            "assignee", "created_by", "project"
        )

    def get_object(self) -> Task:
        task = super().get_object()
        _get_project_for_member(task.project_id, self.request)
        return task


class CommentListCreateView(generics.ListCreateAPIView[Comment]):
    """
    GET  /api/projects/<project_pk>/tasks/<task_pk>/comments/
    POST /api/projects/<project_pk>/tasks/<task_pk>/comments/
    """

    serializer_class = CommentSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        return Comment.objects.filter(task_id=self.kwargs["task_pk"]).select_related("author")

    def get_serializer_context(self) -> dict:
        ctx = super().get_serializer_context()
        ctx["task_id"] = self.kwargs["task_pk"]
        return ctx


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView[Comment]):
    """PATCH / DELETE a comment (author only)."""

    serializer_class = CommentSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        return Comment.objects.filter(task_id=self.kwargs["task_pk"])

    def get_object(self) -> Comment:
        comment = super().get_object()
        if comment.author != self.request.user:
            raise PermissionDenied("You can only edit your own comments.")
        return comment


class MyTasksView(generics.ListAPIView[Task]):
    """GET /api/tasks/me/ – tasks assigned to the current user."""

    serializer_class = TaskListSerializer
    filterset_class = TaskFilter
    search_fields = ["title"]
    ordering_fields = ["due_date", "priority", "status"]

    def get_queryset(self) -> QuerySet[Task]:
        return (
            Task.objects.filter(assignee=self.request.user)
            .select_related("project", "assignee")
            .exclude(status=Task.Status.CANCELLED)
        )
