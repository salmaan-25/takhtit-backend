from django.test import TestCase
from datetime import date, timedelta
from .models import CustomUser, Project, Sprint, Ticket
from .serializers import UserSerializer, ProjectSerializer, SprintSerializer, TicketSerializer


class ModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role='MEMBER'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TST',
            created_by=self.user
        )
        self.sprint = Sprint.objects.create(
            name='Sprint 1',
            project=self.project
        )
        self.ticket = Ticket.objects.create(
            key='TST-1',
            title='First Ticket',
            project=self.project,
            reporter=self.user
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'MEMBER')
        self.assertEqual(str(self.user), 'testuser (MEMBER)')

    def test_project_creation(self):
        self.assertEqual(self.project.key, 'TST')
        self.assertEqual(str(self.project), 'TST - Test Project')

    def test_sprint_creation(self):
        self.assertEqual(self.sprint.project, self.project)
        self.assertEqual(str(self.sprint), 'Sprint 1 (TST)')

    def test_ticket_creation(self):
        self.assertEqual(self.ticket.status, 'TODO')
        self.assertEqual(str(self.ticket), 'TST-1 - First Ticket')


class SerializerTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role='MEMBER'
        )
        self.project = Project.objects.create(
            name='Test Project',
            key='TST',
            created_by=self.user
        )

    def test_user_serializer_valid(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'MEMBER'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_project_serializer_valid(self):
        data = {
            'name': 'New Project',
            'key': 'NEW',
            'description': 'Description'
        }
        serializer = ProjectSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_sprint_serializer_valid_dates(self):
        data = {
            'name': 'Sprint 2',
            'project': self.project.id,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=7),
            'status': 'PLANNED'
        }
        serializer = SprintSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_sprint_serializer_invalid_dates(self):
        data = {
            'name': 'Sprint 3',
            'project': self.project.id,
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=7),
            'status': 'PLANNED'
        }
        serializer = SprintSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_ticket_serializer_valid(self):
        data = {
            'key': 'TST-2',
            'title': 'Test Ticket',
            'project': self.project.id,
            'reporter': self.user.id,
            'status': 'TODO',
            'priority': 'HIGH'
        }
        serializer = TicketSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_ticket_serializer_invalid_status(self):
        data = {
            'key': 'TST-3',
            'title': 'Test Ticket',
            'project': self.project.id,
            'reporter': self.user.id,
            'status': 'INVALID_STATUS',
            'priority': 'LOW'
        }
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_ticket_serializer_invalid_priority(self):
        data = {
            'key': 'TST-4',
            'title': 'Test Ticket',
            'project': self.project.id,
            'reporter': self.user.id,
            'status': 'TODO',
            'priority': 'SUPER_HIGH'
        }
        serializer = TicketSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('priority', serializer.errors)
