import django_filters
from .models import Ticket, Sprint


class TicketFilter(django_filters.FilterSet):
    """
    Allows filtering tickets by exact-match fields.
    Example API calls:
        GET /api/tickets/?status=TODO
        GET /api/tickets/?status=IN_PROGRESS&priority=HIGH
        GET /api/tickets/?project=1
        GET /api/tickets/?assignee=2
        GET /api/tickets/?sprint=1
    """

    class Meta:
        model = Ticket
        fields = ["status", "priority", "project", "sprint", "assignee", "reporter"]


class SprintFilter(django_filters.FilterSet):
    """
    Allows filtering sprints by exact-match fields.
    Example API calls:
        GET /api/sprints/?status=ACTIVE
        GET /api/sprints/?project=1
    """

    class Meta:
        model = Sprint
        fields = ["status", "project"]
