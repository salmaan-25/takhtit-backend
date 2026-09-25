from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

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


def _get_user_org(request):
    """Helper: return the org of the authenticated user, or None."""
    try:
        return request.user.member.organization
    except Exception:
        return None


class ProjectListView(APIView):
    permission_classes = [IsOrgAdminOrReadOnly]
    search_fields = ["name", "key", "description"]
    ordering_fields = ["created_at", "name"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)
        queryset = Project.objects.filter(organization=org)
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        org = _get_user_org(request)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user, organization=org)
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
        project = self.get_object(request, pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Partially update a project (only the sent fields are updated)."""
        project = self.get_object(request, pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a project."""
        project = self.get_object(request, pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SprintListView(APIView):
    permission_classes = [IsOrgMemberCanWrite]
    filterset_class = SprintFilter
    search_fields = ["name"]
    ordering_fields = ["start_date", "end_date", "created_at"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)
        queryset = Sprint.objects.filter(project__organization=org)

        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)

        serializer = SprintSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SprintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SprintDetailView(APIView):
    permission_classes = [IsOrgMemberCanWrite]

    def get_object(self, request, pk):
        org = _get_user_org(request)
        return get_object_or_404(Sprint, pk=pk, project__organization=org)

    def get(self, request, pk):
        sprint = self.get_object(request, pk)
        serializer = SprintSerializer(sprint)
        return Response(serializer.data)

    def patch(self, request, pk):
        sprint = self.get_object(request, pk)
        serializer = SprintSerializer(sprint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sprint = self.get_object(request, pk)
        sprint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketListView(APIView):
    permission_classes = [IsOrgMemberCanWrite]
    filterset_class = TicketFilter
    search_fields = ["title", "description", "key"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        org = _get_user_org(request)
        queryset = Ticket.objects.filter(project__organization=org)

        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)

        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            import uuid

            project = serializer.validated_data["project"]
            ticket = serializer.save(reporter=request.user, key=str(uuid.uuid4())[:20])
            ticket.key = f"{project.key}-{ticket.id}"
            ticket.save(update_fields=["key"])
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
        ticket = self.get_object(request, pk)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    def patch(self, request, pk):
        ticket = self.get_object(request, pk)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = self.get_object(request, pk)
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    """Return a flat list of users in the same org — used for assignee dropdowns."""
    permission_classes = [IsOrgMember]

    def get(self, request):
        from .models import CustomUser
        org = _get_user_org(request)
        # Only return users who belong to the same organization
        users = CustomUser.objects.filter(member__organization=org).order_by("username")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class MeView(APIView):
    """Return the profile of the currently authenticated user, including org and role."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
        queryset = Ticket.objects.filter(assignee=request.user, project__organization=org)

        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)

        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)
