from django.test import TestCase
from django.urls import reverse
from datetime import date, timedelta

from rest_framework.test import APITestCase
from rest_framework import status

from .models import CustomUser, Organization, OrganizationMember, Project, Sprint, Ticket
from .serializers import UserSerializer, ProjectSerializer, SprintSerializer, TicketSerializer


# ===========================================================================
# Helpers
# ===========================================================================

def make_org(name="Acme Corp", slug="acme-corp"):
    return Organization.objects.create(name=name, slug=slug)


def make_user(username="user", password="pass1234", org=None, role="MEMBER"):
    user = CustomUser.objects.create_user(username=username, password=password)
    if org:
        OrganizationMember.objects.create(user=user, organization=org, role=role)
    return user


# ===========================================================================
# Model Tests
# ===========================================================================

class OrganizationModelTests(TestCase):
    def test_organization_str(self):
        org = make_org()
        self.assertEqual(str(org), "Acme Corp")

    def test_organization_member_str(self):
        org = make_org()
        user = make_user(org=org, role="ADMIN")
        member = user.member
        self.assertIn("user", str(member))
        self.assertIn("Acme Corp", str(member))
        self.assertIn("ADMIN", str(member))

    def test_one_user_one_org(self):
        """A user can only belong to one organization (OneToOne)."""
        org1 = make_org(name="Org 1", slug="org-1")
        org2 = make_org(name="Org 2", slug="org-2")
        user = make_user(org=org1)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            OrganizationMember.objects.create(user=user, organization=org2, role="MEMBER")


class ProjectModelTests(TestCase):
    def setUp(self):
        self.org = make_org()
        self.user = make_user(org=self.org, role="ADMIN")
        self.project = Project.objects.create(
            name="Test Project", key="TST", organization=self.org, created_by=self.user
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), "TST - Test Project")

    def test_project_belongs_to_org(self):
        self.assertEqual(self.project.organization, self.org)


# ===========================================================================
# Serializer Tests
# ===========================================================================

class UserSerializerTests(TestCase):
    def test_me_serializer_includes_org_and_role(self):
        org = make_org()
        user = make_user(org=org, role="ADMIN")
        data = UserSerializer(user).data
        self.assertIn("organization", data)
        self.assertIn("role", data)
        self.assertEqual(data["role"], "ADMIN")
        self.assertEqual(data["organization"]["slug"], "acme-corp")

    def test_me_serializer_no_org(self):
        """Users without an org should return None for org and role."""
        user = make_user()  # No org
        data = UserSerializer(user).data
        self.assertIsNone(data["organization"])
        self.assertIsNone(data["role"])


class SprintSerializerTests(TestCase):
    def setUp(self):
        self.org = make_org()
        self.user = make_user(org=self.org, role="ADMIN")
        self.project = Project.objects.create(
            name="Test Project", key="TST", organization=self.org, created_by=self.user
        )

    def test_sprint_serializer_valid_dates(self):
        data = {
            "name": "Sprint 1",
            "project": self.project.id,
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=7),
            "status": "PLANNED",
        }
        serializer = SprintSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_sprint_serializer_invalid_dates(self):
        data = {
            "name": "Sprint Bad",
            "project": self.project.id,
            "start_date": date.today(),
            "end_date": date.today() - timedelta(days=7),
            "status": "PLANNED",
        }
        serializer = SprintSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("end_date", serializer.errors)


# ===========================================================================
# Permission Tests — Core RBAC logic
# ===========================================================================

class PermissionTests(APITestCase):
    def setUp(self):
        self.org = make_org()
        self.admin = make_user(username="admin", org=self.org, role="ADMIN")
        self.member = make_user(username="member", org=self.org, role="MEMBER")
        self.viewer = make_user(username="viewer", org=self.org, role="VIEWER")
        self.no_org_user = make_user(username="orphan")  # No org at all
        self.project = Project.objects.create(
            name="Test Project", key="TST", organization=self.org, created_by=self.admin
        )

    # --- Project creation (Admin only) ---
    def test_admin_can_create_project(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("project-list")
        data = {"name": "New Project", "key": "NEW", "description": "Test"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_cannot_create_project(self):
        self.client.force_authenticate(user=self.member)
        url = reverse("project-list")
        data = {"name": "Should Fail", "key": "FAIL"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_project(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse("project-list")
        data = {"name": "Should Fail", "key": "FAL2"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_without_org_cannot_create_project(self):
        self.client.force_authenticate(user=self.no_org_user)
        url = reverse("project-list")
        data = {"name": "Should Fail", "key": "FAL3"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Project listing (All org members can read) ---
    def test_member_can_list_projects(self):
        self.client.force_authenticate(user=self.member)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_can_list_projects(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Ticket creation (Member and Admin can write, Viewer cannot) ---
    def test_member_can_create_ticket(self):
        self.client.force_authenticate(user=self.member)
        url = reverse("ticket-list")
        data = {
            "title": "A ticket",
            "project": self.project.id,
            "status": "TODO",
            "priority": "MEDIUM",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_create_ticket(self):
        self.client.force_authenticate(user=self.viewer)
        url = reverse("ticket-list")
        data = {
            "title": "Should Fail",
            "project": self.project.id,
            "status": "TODO",
            "priority": "LOW",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ===========================================================================
# Data Isolation Tests — Cross-org leakage prevention
# ===========================================================================

class DataIsolationTests(APITestCase):
    def setUp(self):
        # Org A
        self.org_a = make_org(name="Org A", slug="org-a")
        self.user_a = make_user(username="user_a", org=self.org_a, role="ADMIN")
        self.project_a = Project.objects.create(
            name="Project A", key="ORGA", organization=self.org_a, created_by=self.user_a
        )
        # Org B
        self.org_b = make_org(name="Org B", slug="org-b")
        self.user_b = make_user(username="user_b", org=self.org_b, role="ADMIN")
        self.project_b = Project.objects.create(
            name="Project B", key="ORGB", organization=self.org_b, created_by=self.user_b
        )

    def test_user_a_cannot_see_org_b_projects(self):
        """User from Org A should only see Org A projects."""
        self.client.force_authenticate(user=self.user_a)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [p["key"] for p in response.data]
        self.assertIn("ORGA", keys)
        self.assertNotIn("ORGB", keys)

    def test_user_b_cannot_see_org_a_projects(self):
        """User from Org B should only see Org B projects."""
        self.client.force_authenticate(user=self.user_b)
        url = reverse("project-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        keys = [p["key"] for p in response.data]
        self.assertIn("ORGB", keys)
        self.assertNotIn("ORGA", keys)

    def test_user_a_cannot_access_org_b_project_detail(self):
        """Direct access to another org project should return 404."""
        self.client.force_authenticate(user=self.user_a)
        url = reverse("project-detail", args=[self.project_b.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_list_only_shows_own_org_members(self):
        """Assignee dropdown must not leak users from other orgs."""
        self.client.force_authenticate(user=self.user_a)
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u["username"] for u in response.data]
        self.assertIn("user_a", usernames)
        self.assertNotIn("user_b", usernames)


# ===========================================================================
# Me Endpoint Tests
# ===========================================================================

class MeViewTests(APITestCase):
    def test_me_returns_org_and_role(self):
        org = make_org()
        user = make_user(username="me_user", org=org, role="MEMBER")
        self.client.force_authenticate(user=user)
        url = reverse("me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "MEMBER")
        self.assertIsNotNone(response.data["organization"])
        self.assertEqual(response.data["organization"]["name"], "Acme Corp")

    def test_me_unauthenticated_returns_401(self):
        url = reverse("me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ===========================================================================
# Filtering Tests (still work within org scope)
# ===========================================================================

class FilteringTests(APITestCase):
    def setUp(self):
        self.org = make_org()
        self.user = make_user(username="filteruser", org=self.org, role="MEMBER")
        self.project = Project.objects.create(
            name="Filter Project", key="FLT", organization=self.org, created_by=self.user
        )
        self.ticket_todo = Ticket.objects.create(
            key="FLT-1", title="Todo ticket",
            project=self.project, reporter=self.user, status="TODO", priority="HIGH",
        )
        self.ticket_done = Ticket.objects.create(
            key="FLT-2", title="Done ticket",
            project=self.project, reporter=self.user, status="DONE", priority="LOW",
        )
        self.client.force_authenticate(user=self.user)

    def test_filter_tickets_by_status(self):
        url = reverse("ticket-list")
        response = self.client.get(url, {"status": "TODO"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "TODO")

    def test_search_tickets(self):
        url = reverse("ticket-list")
        response = self.client.get(url, {"search": "Done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["key"], "FLT-2")
