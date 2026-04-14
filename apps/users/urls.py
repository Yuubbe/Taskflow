from django.urls import path

from apps.users.views import MeView, RegisterView, UserDetailView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("users/me/", MeView.as_view(), name="me"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
