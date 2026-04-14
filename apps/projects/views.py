"""Project views."""

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project, ProjectMembership
from apps.projects.permissions import IsProjectAdmin, IsProjectMember
from apps.projects.serializers import AddMemberSerializer, ProjectMembershipSerializer, ProjectSerializer
from apps.users.models import User


class ProjectListCreateView(generics.ListCreateAPIView[Project]):
    """
    GET  /api/projects/  – list projects the user is a member of.
    POST /api/projects/  – create a new project (caller becomes owner + admin).
    """

    serializer_class = ProjectSerializer

    def get_queryset(self) -> QuerySet[Project]:
        return Project.objects.filter(members=self.request.user).select_related("owner")


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView[Project]):
    """
    GET    /api/projects/<pk>/
    PATCH  /api/projects/<pk>/
    DELETE /api/projects/<pk>/
    """

    serializer_class = ProjectSerializer
    queryset = Project.objects.select_related("owner")

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [permissions.IsAuthenticated(), IsProjectAdmin()]
        return [permissions.IsAuthenticated(), IsProjectMember()]


class ProjectMembersView(APIView):
    """
    GET  /api/projects/<pk>/members/  – list members.
    POST /api/projects/<pk>/members/  – add a member (admin only).
    """

    def _get_project(self, pk: int, request: Request) -> Project:
        project = get_object_or_404(Project, pk=pk)
        if not project.memberships.filter(user=request.user).exists():
            self.permission_denied(request)
        return project

    def get(self, request: Request, pk: int) -> Response:
        project = self._get_project(pk, request)
        memberships = project.memberships.select_related("user").all()
        serializer = ProjectMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request: Request, pk: int) -> Response:
        project = get_object_or_404(Project, pk=pk)
        # Only admins can add members
        is_admin = project.memberships.filter(user=request.user, role=ProjectMembership.Role.ADMIN).exists()
        if not is_admin and project.owner != request.user:
            return Response({"detail": "You must be a project admin to add members."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, pk=serializer.validated_data["user_id"])
        membership, created = ProjectMembership.objects.get_or_create(
            user=user,
            project=project,
            defaults={"role": serializer.validated_data["role"]},
        )
        if not created:
            return Response({"detail": "User is already a member."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ProjectMembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class RemoveMemberView(APIView):
    """DELETE /api/projects/<pk>/members/<user_pk>/"""

    def delete(self, request: Request, pk: int, user_pk: int) -> Response:
        project = get_object_or_404(Project, pk=pk)
        is_admin = project.memberships.filter(user=request.user, role=ProjectMembership.Role.ADMIN).exists()
        if not is_admin and project.owner != request.user:
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        membership = get_object_or_404(ProjectMembership, project=project, user_id=user_pk)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
