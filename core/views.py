from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from .models import Project, Sprint, Ticket
from .serializers import (
    ProjectSerializer,
    SprintSerializer,
    TicketSerializer,
    UserSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer
from .filters import TicketFilter, SprintFilter
from .permissions import IsOrgAdminOrReadOnly, IsOrgMemberCanWrite, IsOrgMember


# ---------------------------------------------------------------------------
# Cache TTL constants (in seconds)
# ---------------------------------------------------------------------------
CACHE_TTL_SHORT = 60 * 2    # 2 minutes  – for frequently-mutated lists
CACHE_TTL_MEDIUM = 60 * 5   # 5 minutes  – for detail views
CACHE_TTL_LONG = 60 * 30    # 30 minutes – for near-static data (users list)


# ---------------------------------------------------------------------------
# Cache key helpers – keyed by org so users never see each other's data
# ---------------------------------------------------------------------------
def _projects_list_key(org_id):
    return f"org:{org_id}:projects"


def _project_detail_key(org_id, pk):
    return f"org:{org_id}:project:{pk}"


def _sprints_list_key(org_id):
    return f"org:{org_id}:sprints"


def _sprint_detail_key(org_id, pk):
    return f"org:{org_id}:sprint:{pk}"


def _tickets_list_key(org_id):
    return f"org:{org_id}:tickets"


def _ticket_detail_key(org_id, pk):
    return f"org:{org_id}:ticket:{pk}"


def _users_list_key(org_id):
    return f"org:{org_id}:users"


def _my_tickets_key(org_id, user_id):
    return f"org:{org_id}:user:{user_id}:my_tickets"


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------
def _get_user_org(request):
    """Helper: return the org of the authenticated user, or None."""
    try:
        return request.user.member.organization
    except Exception:
        return None


# ===========================================================================
# Projects
# ===========================================================================

class ProjectListView(APIView):
    permission_classes = [IsOrgAdminOrReadOnly]
    search_fields = ["name", "key", "description"]
    ordering_fields = ["created_at", "name"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)

        # Only use cache when there are NO query params (filters bypass cache)
        if not request.query_params:
            cache_key = _projects_list_key(org.id)
            cached = cache.get(cache_key)
            if cached is not None:
                print("CACHE HIT – projects list")
                return Response(cached)

        print("CACHE MISS – projects list")
        queryset = Project.objects.filter(organization=org)
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = ProjectSerializer(queryset, many=True)
        data = serializer.data

        if not request.query_params:
            cache.set(_projects_list_key(org.id), data, timeout=CACHE_TTL_SHORT)

        return Response(data)

    def post(self, request):
        org = _get_user_org(request)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, organization=org)
            # Invalidate projects list for this org
            cache.delete(_projects_list_key(org.id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [IsOrgAdminOrReadOnly]

    def get_object(self, request, pk):
        """Fetch project by ID scoped to the user's org, or return 404."""
        org = _get_user_org(request)
        return get_object_or_404(Project, pk=pk, organization=org)

    def get(self, request, pk):
        """Return a single project."""
        org = _get_user_org(request)
        cache_key = _project_detail_key(org.id, pk)
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"CACHE HIT – project:{pk}")
            return Response(cached)

        print(f"CACHE MISS – project:{pk}")
        project = self.get_object(request, pk)
        serializer = ProjectSerializer(project)
        data = serializer.data
        cache.set(cache_key, data, timeout=CACHE_TTL_MEDIUM)
        return Response(data)

    def patch(self, request, pk):
        """Partially update a project (only the sent fields are updated)."""
        org = _get_user_org(request)
        project = self.get_object(request, pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Invalidate both the detail and list caches
            cache.delete(_project_detail_key(org.id, pk))
            cache.delete(_projects_list_key(org.id))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a project."""
        org = _get_user_org(request)
        project = self.get_object(request, pk)
        project.delete()
        # Invalidate both the detail and list caches
        cache.delete(_project_detail_key(org.id, pk))
        cache.delete(_projects_list_key(org.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================================================================
# Sprints
# ===========================================================================

class SprintListView(APIView):
    permission_classes = [IsOrgMemberCanWrite]
    filterset_class = SprintFilter
    search_fields = ["name"]
    ordering_fields = ["start_date", "end_date", "created_at"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)

        if not request.query_params:
            cache_key = _sprints_list_key(org.id)
            cached = cache.get(cache_key)
            if cached is not None:
                print("CACHE HIT – sprints list")
                return Response(cached)

        print("CACHE MISS – sprints list")
        queryset = Sprint.objects.filter(project__organization=org)
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = SprintSerializer(queryset, many=True)
        data = serializer.data

        if not request.query_params:
            cache.set(_sprints_list_key(org.id), data, timeout=CACHE_TTL_SHORT)

        return Response(data)

    def post(self, request):
        org = _get_user_org(request)
        serializer = SprintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(_sprints_list_key(org.id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SprintDetailView(APIView):
    permission_classes = [IsOrgMemberCanWrite]

    def get_object(self, request, pk):
        org = _get_user_org(request)
        return get_object_or_404(Sprint, pk=pk, project__organization=org)

    def get(self, request, pk):
        org = _get_user_org(request)
        cache_key = _sprint_detail_key(org.id, pk)
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"CACHE HIT – sprint:{pk}")
            return Response(cached)

        print(f"CACHE MISS – sprint:{pk}")
        sprint = self.get_object(request, pk)
        serializer = SprintSerializer(sprint)
        data = serializer.data
        cache.set(cache_key, data, timeout=CACHE_TTL_MEDIUM)
        return Response(data)

    def patch(self, request, pk):
        org = _get_user_org(request)
        sprint = self.get_object(request, pk)
        serializer = SprintSerializer(sprint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(_sprint_detail_key(org.id, pk))
            cache.delete(_sprints_list_key(org.id))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        org = _get_user_org(request)
        sprint = self.get_object(request, pk)
        sprint.delete()
        cache.delete(_sprint_detail_key(org.id, pk))
        cache.delete(_sprints_list_key(org.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================================================================
# Tickets
# ===========================================================================

class TicketListView(APIView):
    permission_classes = [IsOrgMemberCanWrite]
    filterset_class = TicketFilter
    search_fields = ["title", "description", "key"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)

        if not request.query_params:
            cache_key = _tickets_list_key(org.id)
            cached = cache.get(cache_key)
            if cached is not None:
                print("CACHE HIT – tickets list")
                return Response(cached)

        print("CACHE MISS – tickets list")
        queryset = Ticket.objects.filter(project__organization=org)
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = TicketSerializer(queryset, many=True)
        data = serializer.data

        if not request.query_params:
            cache.set(_tickets_list_key(org.id), data, timeout=CACHE_TTL_SHORT)

        return Response(data)

    def post(self, request):
        import uuid
        org = _get_user_org(request)
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.validated_data["project"]
            ticket = serializer.save(reporter=request.user, key=str(uuid.uuid4())[:20])
            ticket.key = f"{project.key}-{ticket.id}"
            ticket.save(update_fields=["key"])
            # Invalidate list + my_tickets for the reporter
            cache.delete(_tickets_list_key(org.id))
            cache.delete(_my_tickets_key(org.id, request.user.id))
            return Response(
                TicketSerializer(ticket).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailView(APIView):
    permission_classes = [IsOrgMemberCanWrite]

    def get_object(self, request, pk):
        org = _get_user_org(request)
        return get_object_or_404(Ticket, pk=pk, project__organization=org)

    def get(self, request, pk):
        org = _get_user_org(request)
        cache_key = _ticket_detail_key(org.id, pk)
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"CACHE HIT – ticket:{pk}")
            return Response(cached)

        print(f"CACHE MISS – ticket:{pk}")
        ticket = self.get_object(request, pk)
        serializer = TicketSerializer(ticket)
        data = serializer.data
        cache.set(cache_key, data, timeout=CACHE_TTL_MEDIUM)
        return Response(data)

    def patch(self, request, pk):
        org = _get_user_org(request)
        ticket = self.get_object(request, pk)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(_ticket_detail_key(org.id, pk))
            cache.delete(_tickets_list_key(org.id))
            # If ticket is reassigned, old + new assignee's my_tickets are stale
            cache.delete(_my_tickets_key(org.id, ticket.assignee_id or 0))
            cache.delete(_my_tickets_key(org.id, request.user.id))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        org = _get_user_org(request)
        ticket = self.get_object(request, pk)
        assignee_id = ticket.assignee_id
        ticket.delete()
        cache.delete(_ticket_detail_key(org.id, pk))
        cache.delete(_tickets_list_key(org.id))
        cache.delete(_my_tickets_key(org.id, assignee_id or 0))
        cache.delete(_my_tickets_key(org.id, request.user.id))
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================================================================
# Auth & User views (no caching needed for write operations)
# ===========================================================================

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Anyone can register without a token!

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """Return a flat list of users in the same org – used for assignee dropdowns."""
    permission_classes = [IsOrgMember]

    def get(self, request):
        from .models import CustomUser
        org = _get_user_org(request)

        cache_key = _users_list_key(org.id)
        cached = cache.get(cache_key)
        if cached is not None:
            print("CACHE HIT – users list")
            return Response(cached)

        print("CACHE MISS – users list")
        users = CustomUser.objects.filter(member__organization=org).order_by("username")
        serializer = UserSerializer(users, many=True)
        data = serializer.data
        # Users list changes rarely – use a longer TTL
        cache.set(cache_key, data, timeout=CACHE_TTL_LONG)
        return Response(data)


class MeView(APIView):
    """Return the profile of the currently authenticated user, including org and role."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Never cache /me – it's always user-specific and changes with auth state
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class MyTicketsView(APIView):
    """
    Return tickets assigned to the currently authenticated user,
    scoped to their organization.
    """
    permission_classes = [IsOrgMember]
    filterset_class = TicketFilter
    search_fields = ["title", "description", "key"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)

        if not request.query_params:
            cache_key = _my_tickets_key(org.id, request.user.id)
            cached = cache.get(cache_key)
            if cached is not None:
                print(f"CACHE HIT – my_tickets user:{request.user.id}")
                return Response(cached)

        print(f"CACHE MISS – my_tickets user:{request.user.id}")
        queryset = Ticket.objects.filter(assignee=request.user, project__organization=org)
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = TicketSerializer(queryset, many=True)
        data = serializer.data

        if not request.query_params:
            cache.set(_my_tickets_key(org.id, request.user.id), data, timeout=CACHE_TTL_SHORT)

        return Response(data)
