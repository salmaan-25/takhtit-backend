from django.urls import path
from .views import (
    ProjectListView,
    ProjectDetailView,
    SprintListView,
    SprintDetailView,
    TicketListView,
    TicketDetailView,
    RegisterView,
    UserListView,
    MeView,
    MyTicketsView,
)

urlpatterns = [
    # Project endpoints
    path("projects/", ProjectListView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    # Sprint endpoints
    path("sprints/", SprintListView.as_view(), name="sprint-list"),
    path("sprints/<int:pk>/", SprintDetailView.as_view(), name="sprint-detail"),
    # Ticket endpoints
    path("tickets/", TicketListView.as_view(), name="ticket-list"),
    path("tickets/<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("tickets/my/", MyTicketsView.as_view(), name="my-tickets"),
]
