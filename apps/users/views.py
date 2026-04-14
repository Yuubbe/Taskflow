"""User views."""

from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import RegisterSerializer, UpdateProfileSerializer, UserSerializer


class RegisterView(generics.CreateAPIView[User]):
    """POST /api/auth/register/ – create a new user account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """GET / PATCH /api/users/me/ – authenticated user's profile."""

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class UserDetailView(generics.RetrieveAPIView[User]):
    """GET /api/users/<pk>/ – public profile."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
