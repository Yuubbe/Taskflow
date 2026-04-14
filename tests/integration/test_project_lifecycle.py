"""Integration tests – full project lifecycle."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import ProjectMembership
from tests.factories import UserFactory


def auth_client(user) -> APIClient:
    c = APIClient()
    resp = c.post(reverse("token_obtain_pair"), {"email": user.email, "password": "testpass123"})
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return c


@pytest.mark.django_db
class TestProjectLifecycle:
    """Full workflow: create project → add member → create task → comment."""

    def test_full_workflow(self) -> None:
        owner = UserFactory()
        contributor = UserFactory()
        owner_client = auth_client(owner)
        contrib_client = auth_client(contributor)

        # 1. Create project
        resp = owner_client.post(reverse("project-list"), {"name": "Alpha", "description": "Our first project"})
        assert resp.status_code == status.HTTP_201_CREATED
        project_id = resp.data["id"]

        # 2. Owner can see the project
        resp = owner_client.get(reverse("project-detail", kwargs={"pk": project_id}))
        assert resp.status_code == status.HTTP_200_OK

        # 3. Add contributor as member
        resp = owner_client.post(
            reverse("project-members", kwargs={"pk": project_id}),
            {"user_id": contributor.pk, "role": ProjectMembership.Role.CONTRIBUTOR},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # 4. Contributor creates a task
        task_url = reverse("task-list", kwargs={"project_pk": project_id})
        resp = contrib_client.post(task_url, {"title": "Build login", "priority": "high"})
        assert resp.status_code == status.HTTP_201_CREATED
        task_id = resp.data["id"]

        # 5. Owner assigns task to contributor
        detail_url = reverse("task-detail", kwargs={"project_pk": project_id, "pk": task_id})
        resp = owner_client.patch(detail_url, {"assignee_id": contributor.pk, "status": "in_progress"})
        assert resp.status_code == status.HTTP_200_OK

        # 6. Contributor posts a comment
        comment_url = reverse("comment-list", kwargs={"project_pk": project_id, "task_pk": task_id})
        resp = contrib_client.post(comment_url, {"body": "Starting this now!"})
        assert resp.status_code == status.HTTP_201_CREATED

        # 7. Contributor can see their assigned task in /api/tasks/me/
        resp = contrib_client.get(reverse("my-tasks"))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["id"] == task_id

        # 8. Stranger cannot list project tasks
        stranger = UserFactory()
        stranger_client = auth_client(stranger)
        resp = stranger_client.get(task_url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
