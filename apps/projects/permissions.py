"""Custom permissions for projects."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.projects.models import Project, ProjectMembership


class IsProjectMember(BasePermission):
    """Allow access only to project members."""

    def has_object_permission(self, request: Request, view: APIView, obj: Project) -> bool:
        return obj.memberships.filter(user=request.user).exists()


class IsProjectAdmin(BasePermission):
    """Allow write access only to project admins or owner."""

    def has_object_permission(self, request: Request, view: APIView, obj: Project) -> bool:
        if obj.owner == request.user:
            return True
        return obj.memberships.filter(user=request.user, role=ProjectMembership.Role.ADMIN).exists()
