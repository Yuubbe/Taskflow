"""Shared test factories."""

import factory
from factory.django import DjangoModelFactory

from apps.projects.models import Project, ProjectMembership
from apps.tasks.models import Comment, Task
from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")

    @factory.post_generation  # type: ignore[misc]
    def password(obj: User, create: bool, extracted: str | None, **kwargs: object) -> None:
        pwd = extracted if extracted is not None else "testpass123"
        obj.set_password(pwd)
        if create:
            obj.save()


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Project {n}")
    owner = factory.SubFactory(UserFactory)

    @factory.post_generation  # type: ignore[misc]
    def with_owner_membership(obj: Project, create: bool, extracted: bool, **kwargs: object) -> None:
        if create:
            ProjectMembership.objects.get_or_create(
                user=obj.owner,
                project=obj,
                defaults={"role": ProjectMembership.Role.ADMIN},
            )


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    project = factory.SubFactory(ProjectFactory)
    created_by = factory.SubFactory(UserFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    task = factory.SubFactory(TaskFactory)
    author = factory.SubFactory(UserFactory)
    body = factory.Faker("sentence")
