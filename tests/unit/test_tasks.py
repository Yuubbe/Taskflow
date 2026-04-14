"""Unit tests – Task CRUD & filters."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import ProjectMembership
from apps.tasks.models import Task
from tests.factories import ProjectFactory, TaskFactory, UserFactory


def make_auth_client(user=None) -> tuple[APIClient, object]:
    if user is None:
        user = UserFactory()
    client = APIClient()
    resp = client.post(reverse("token_obtain_pair"), {"email": user.email, "password": "testpass123"})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return client, user


@pytest.mark.django_db
class TestTaskCRUD:
    def setup_method(self) -> None:
        self.owner = UserFactory()
        self.project = ProjectFactory(owner=self.owner)
        self.client, _ = make_auth_client(self.owner)

    def _list_url(self) -> str:
        return reverse("task-list", kwargs={"project_pk": self.project.pk})

    def _detail_url(self, pk: int) -> str:
        return reverse("task-detail", kwargs={"project_pk": self.project.pk, "pk": pk})

    def test_create_task(self) -> None:
        payload = {"title": "My first task", "priority": "high"}
        response = self.client.post(self._list_url(), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title="My first task").exists()

    def test_list_tasks(self) -> None:
        TaskFactory.create_batch(3, project=self.project)
        response = self.client.get(self._list_url())
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 3

    def test_filter_by_status(self) -> None:
        TaskFactory(project=self.project, status=Task.Status.DONE)
        TaskFactory(project=self.project, status=Task.Status.TODO)
        response = self.client.get(self._list_url() + "?status=done")
        assert response.status_code == status.HTTP_200_OK
        assert all(t["status"] == "done" for t in response.data["results"])

    def test_update_task_status(self) -> None:
        task = TaskFactory(project=self.project)
        response = self.client.patch(self._detail_url(task.pk), {"status": "in_progress"})
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == Task.Status.IN_PROGRESS

    def test_delete_task(self) -> None:
        task = TaskFactory(project=self.project)
        response = self.client.delete(self._detail_url(task.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_non_member_cannot_create(self) -> None:
        stranger_client, _ = make_auth_client()
        response = stranger_client.post(self._list_url(), {"title": "Hack"})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMyTasks:
    def test_returns_only_assigned_tasks(self) -> None:
        user = UserFactory()
        client, _ = make_auth_client(user)
        project = ProjectFactory(owner=user)
        TaskFactory(project=project, assignee=user)
        TaskFactory(project=project)  # not assigned to user
        response = client.get(reverse("my-tasks"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
