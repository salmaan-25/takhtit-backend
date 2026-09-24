from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, Sprint, Ticket


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("role", "is_active", "is_staff")

    # Add 'role' to the default UserAdmin fieldsets
    fieldsets = UserAdmin.fieldsets + (("Custom Fields", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "created_by", "created_at")
    search_fields = ("name", "key")
    list_select_related = ("created_by",)
    raw_id_fields = ("created_by",)


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "start_date", "end_date", "status")
    search_fields = ("name", "project__name", "project__key")
    list_filter = ("status", "project")
    list_select_related = ("project",)
    raw_id_fields = ("project",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "title",
        "project",
        "sprint",
        "status",
        "priority",
        "assignee",
    )
    search_fields = ("key", "title", "description")
    list_filter = ("status", "priority", "project", "sprint")
    list_select_related = ("project", "sprint", "reporter", "assignee")
    raw_id_fields = ("project", "sprint", "reporter", "assignee")
