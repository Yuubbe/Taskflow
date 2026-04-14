"""Task filters."""

import django_filters

from apps.tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    due_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    due_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = {
            "status": ["exact"],
            "priority": ["exact"],
            "assignee": ["exact"],
            "project": ["exact"],
        }
