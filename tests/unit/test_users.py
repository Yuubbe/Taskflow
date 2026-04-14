"""Unit tests – User registration & profile."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from tests.factories import UserFactory


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_client(client: APIClient) -> APIClient:
    user = UserFactory()
    response = client.post(
        reverse("token_obtain_pair"),
        {"email": user.email, "password": "testpass123"},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    client._user = user  # type: ignore[attr-defined]
    return client


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client: APIClient) -> None:
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = client.post(reverse("register"), payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_password_mismatch(self, client: APIClient) -> None:
        payload = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass!",
        }
        response = client.post(reverse("register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, client: APIClient) -> None:
        existing = UserFactory()
        payload = {
            "username": "another",
            "email": existing.email,
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        response = client.post(reverse("register"), payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfile:
    def test_get_me(self, auth_client: APIClient) -> None:
        response = auth_client.get(reverse("me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == auth_client._user.email  # type: ignore[attr-defined]

    def test_patch_bio(self, auth_client: APIClient) -> None:
        response = auth_client.patch(reverse("me"), {"bio": "Hello world"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Hello world"

    def test_me_unauthenticated(self, client: APIClient) -> None:
        response = client.get(reverse("me"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
