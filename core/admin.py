from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Organization, OrganizationMember, Project, Sprint, Ticket


# ---------------------------------------------------------------------------
# Organization Admin
# ---------------------------------------------------------------------------

class OrganizationMemberInline(admin.TabularInline):
    """Shows all members of an org inline on the Organization page."""
    model = OrganizationMember
    extra = 1
    fields = ("user", "role", "joined_at")
    readonly_fields = ("joined_at",)
    autocomplete_fields = ["user"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "member_count", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # Auto-fills slug from name
    inlines = [OrganizationMemberInline]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = "Members"


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "joined_at")
    list_filter = ("role", "organization")
    search_fields = ("user__username", "user__email", "organization__name")
    autocomplete_fields = ["user", "organization"]


# ---------------------------------------------------------------------------
# Custom User Admin
# ---------------------------------------------------------------------------

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "get_org", "get_role", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")

    def get_org(self, obj):
        try:
            return obj.member.organization.name
        except Exception:
            return "—"
    get_org.short_description = "Organization"

    def get_role(self, obj):
        try:
            return obj.member.role
        except Exception:
            return "—"
    get_role.short_description = "Role"


# ---------------------------------------------------------------------------
# Project / Sprint / Ticket Admin
# ---------------------------------------------------------------------------

class SprintInline(admin.TabularInline):
    model = Sprint
    extra = 0
    fields = ("name", "status", "start_date", "end_date")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "organization", "created_by", "created_at")
    list_filter = ("organization",)
    search_fields = ("name", "key", "organization__name")
    inlines = [SprintInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "start_date", "end_date")
    list_filter = ("status", "project__organization")
    search_fields = ("name", "project__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "project", "status", "priority", "assignee", "reporter")
    list_filter = ("status", "priority", "project__organization", "project")
    search_fields = ("key", "title", "assignee__username", "reporter__username")
    readonly_fields = ("key", "created_at", "updated_at")
    autocomplete_fields = ["assignee", "reporter"]
