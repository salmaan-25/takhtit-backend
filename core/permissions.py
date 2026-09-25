from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    """
    Allows access only to users who are linked to an Organization.
    Any user without an OrganizationMember record is denied.
    """
    message = "You must belong to an organization to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "member")
        )


class IsOrgAdmin(BasePermission):
    """
    Allows access only to users with the ADMIN role in their organization.
    Used for sensitive operations like creating/deleting projects.
    """
    message = "Only organization admins can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "member")
            and request.user.member.role == "ADMIN"
        )


class IsOrgAdminOrReadOnly(BasePermission):
    """
    Read-only for any org member; write operations require ADMIN role.
    """
    message = "Only organization admins can modify this resource."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, "member")):
            return False
        # Safe methods (GET, HEAD, OPTIONS) are allowed for any member
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        # Write methods require ADMIN role
        return request.user.member.role == "ADMIN"


class IsOrgMemberCanWrite(BasePermission):
    """
    Read-only for VIEWER; MEMBER and ADMIN can write.
    Used for Ticket and Sprint creation.
    """
    message = "Viewers cannot create or modify resources."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, "member")):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.member.role in ("ADMIN", "MEMBER")
