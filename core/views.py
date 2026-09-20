from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Project, Sprint, Ticket
from .serializers import ProjectSerializer, SprintSerializer, TicketSerializer
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from .filters import TicketFilter, SprintFilter


class ProjectListView(APIView):
    search_fields = ["name", "key", "description"]
    ordering_fields = ["created_at", "name"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        queryset = Project.objects.all()
        # Apply each filter backend manually
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):

    def get_object(self, pk):
        """Helper method: fetch a project by ID or return 404."""
        return get_object_or_404(Project, pk=pk)

    def get(self, request, pk):
        """Return a single project."""
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Partially update a project (only the sent fields are updated)."""
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a project."""
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SprintListView(APIView):
    filterset_class = SprintFilter
    search_fields = ["name"]
    ordering_fields = ["start_date", "end_date", "created_at"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        queryset = Sprint.objects.all()

        # Apply each filter backend manually
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

    def get_object(self, pk):
        return get_object_or_404(Sprint, pk=pk)

    def get(self, request, pk):
        sprint = self.get_object(pk)
        serializer = SprintSerializer(sprint)
        return Response(serializer.data)

    def patch(self, request, pk):
        sprint = self.get_object(pk)
        serializer = SprintSerializer(sprint, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sprint = self.get_object(pk)
        sprint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketListView(APIView):
    filterset_class = TicketFilter
    search_fields = ["title", "description", "key"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]

    def get(self, request):
        from django_filters.rest_framework import DjangoFilterBackend
        from rest_framework.filters import SearchFilter, OrderingFilter

        queryset = Ticket.objects.all()

        # Apply each filter backend manually
        for backend in [DjangoFilterBackend(), SearchFilter(), OrderingFilter()]:
            queryset = backend.filter_queryset(request, queryset, self)

        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailView(APIView):

    def get_object(self, pk):
        return get_object_or_404(Ticket, pk=pk)

    def get(self, request, pk):
        ticket = self.get_object(pk)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    def patch(self, request, pk):
        ticket = self.get_object(pk)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = self.get_object(pk)
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
