from django.urls import path

from apps.projects.views import ProjectDetailView, ProjectListCreateView, ProjectMembersView, RemoveMemberView

urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("projects/<int:pk>/members/", ProjectMembersView.as_view(), name="project-members"),
    path("projects/<int:pk>/members/<int:user_pk>/", RemoveMemberView.as_view(), name="project-remove-member"),
]
