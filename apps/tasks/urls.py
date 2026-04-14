from django.urls import path

from apps.tasks.views import CommentDetailView, CommentListCreateView, MyTasksView, TaskDetailView, TaskListCreateView

urlpatterns = [
    path("tasks/me/", MyTasksView.as_view(), name="my-tasks"),
    path("projects/<int:project_pk>/tasks/", TaskListCreateView.as_view(), name="task-list"),
    path("projects/<int:project_pk>/tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("projects/<int:project_pk>/tasks/<int:task_pk>/comments/", CommentListCreateView.as_view(), name="comment-list"),
    path("projects/<int:project_pk>/tasks/<int:task_pk>/comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
]
