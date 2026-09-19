# Takhtit — Backend

A simplified JIRA-inspired project management backend built with **Django REST Framework and PostgreSQL**.

TaskFlow allows users to create and manage projects, plan sprints, create and assign tickets, and track ticket progress through different statuses.

The project is intentionally smaller than JIRA and focuses on the essential concepts required to understand and build a real-world REST API.

---

# 1. Project Overview

TaskFlow is a project management system where users can:

- Create and manage projects
- Create and manage sprints
- Create and manage tickets/tasks
- Assign tickets to users
- Report tickets
- Add tickets to sprints
- Set ticket priorities
- Move tickets through different statuses
- View project, sprint, and ticket information

The backend will expose REST APIs that will later be consumed by a React frontend.

## High-Level Architecture

```text
React Frontend
      |
      | HTTP / REST API
      ↓
Django REST Framework
      |
      ├── APIView
      ├── Serializers
      ├── Validation
      └── Business Logic
      |
      ↓
Django ORM
      |
      ↓
PostgreSQL
```

---

# 2. Technology Stack

## Backend

- Python
- Django
- Django REST Framework
- PostgreSQL

## Frontend

The frontend will be developed separately after completing the backend.

- React
- JavaScript / TypeScript
- Axios or Fetch API

## Development Tools

- Git
- Postman
- VS Code
- PostgreSQL client / pgAdmin

---

# 3. Core Features

## Project Management

Users can:

- Create a project
- View projects
- View project details
- Update project information
- Delete projects

Example:

```text
TaskFlow
TF

Description:
Internal project management application
```

---

## Sprint Management

Users can:

- Create a sprint
- Associate a sprint with a project
- Set start and end dates
- Add tickets to a sprint
- View sprint details
- Update sprint information
- Delete a sprint

Sprint statuses:

```text
PLANNED
ACTIVE
COMPLETED
```

---

## Ticket Management

Tickets are the main work items in TaskFlow.

A ticket contains:

- Ticket ID
- Ticket key
- Title
- Description
- Project
- Reporter
- Assignee
- Sprint
- Status
- Priority
- Created date
- Updated date

Example:

```text
TF-101

Title:
Implement Login API

Description:
Create login API using Django REST Framework.

Reporter:
Asif

Assignee:
Mohamed

Sprint:
Sprint 1

Status:
IN_PROGRESS

Priority:
HIGH
```

---

# 4. Ticket Workflow

Tickets will move through a simple workflow.

```text
TODO
  ↓
IN_PROGRESS
  ↓
IN_REVIEW
  ↓
DONE
```

The frontend will eventually display these statuses as columns in a Kanban-style board.

Example:

```text
┌────────────┬───────────────┬────────────┬──────────┐
│    TODO    │  IN_PROGRESS  │ IN_REVIEW  │   DONE   │
├────────────┼───────────────┼────────────┼──────────┤
│ TF-101     │ TF-104        │ TF-108     │ TF-102   │
│ Login API  │ Auth API      │ UI Review  │ Navbar   │
│            │               │            │          │
│ TF-103     │ TF-105        │            │ TF-106   │
│ Dashboard  │ User API      │            │ Footer   │
└────────────┴───────────────┴────────────┴──────────┘
```

---

# 5. Ticket Priority

Tickets will support four priority levels:

```text
LOW
MEDIUM
HIGH
URGENT
```

---

# 6. Database Design

The initial version will contain four core entities:

```text
User
Project
Sprint
Ticket
```

---

## User

Django's authentication/user system will be used rather than storing passwords manually.

Conceptually:

```text
User
----------------
id
username
email
password
first_name
last_name
role
```

Roles for the initial version:

```text
ADMIN
MEMBER
```

Authentication-specific fields will be handled by Django.

---

## Project

```text
Project
----------------
id
name
key
description
created_by
created_at
updated_at
```

Example:

```text
id: 1
name: TaskFlow
key: TF
description: Internal project management application
created_by: Mohamed
```

The project key can be used to generate ticket identifiers:

```text
TF-1
TF-2
TF-3
```

---

## Sprint

```text
Sprint
----------------
id
name
project
start_date
end_date
status
created_at
updated_at
```

Example:

```text
Sprint 1
Project: TaskFlow
Start: 2026-09-20
End: 2026-10-04
Status: ACTIVE
```

Relationship:

```text
Project
   |
   └── has many Sprints
```

---

## Ticket

```text
Ticket
-------------------------
id
key
title
description
project
assignee
reporter
sprint
status
priority
created_at
updated_at
```

Relationships:

```text
Ticket
  |
  ├── Project
  ├── Assignee → User
  ├── Reporter → User
  └── Sprint
```

A ticket can initially exist without a sprint.

This allows a backlog workflow:

```text
Create Ticket
      ↓
   Backlog
      ↓
Sprint Planning
      ↓
   Sprint 1
```

Therefore, the sprint relationship can be optional.

---

# 7. Database Relationships

The overall relationship will be:

```text
                    USER
                  /      \
                 /        \
           reporter      assignee
               |            |
               └─────┬──────┘
                     |
                   TICKET
                  /      \
                 /        \
                /          \
           PROJECT        SPRINT
              |              |
              |              |
          has many        has many
           tickets         tickets
              |              |
              └──────┬───────┘
                     |
                   PROJECT
```

More specifically:

```text
User
 └──< Ticket (reporter)

User
 └──< Ticket (assignee)

Project
 ├──< Ticket
 └──< Sprint

Sprint
 └──< Ticket
```

---

# 8. Backend Development Plan

The backend will be developed first.

The React frontend will be developed after the backend APIs are stable.

## Phase 1 — Django Setup

Create:

- Virtual environment
- Django project
- Django application
- DRF installation
- PostgreSQL database connection
- Environment configuration

---

# 9. Models

Create Django models for:

```text
User
Project
Sprint
Ticket
```

Use Django ORM and migrations to create the PostgreSQL database structure.

Important Django concepts:

- Models
- Fields
- ForeignKey
- Choices
- `on_delete`
- Migrations
- ORM queries

---

# 10. Serializers

Create DRF serializers using `ModelSerializer`.

Expected serializers:

```text
UserSerializer
ProjectSerializer
SprintSerializer
TicketSerializer
```

Serializers will handle:

- Model → JSON conversion
- JSON → Python/model data conversion
- Input validation
- Field validation
- Business-related validation where appropriate

Example:

```python
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
```

Validation will be added as the project requirements become more specific.

---

# 11. API Views

The initial implementation will use:

```python
APIView
```

because APIView provides a clear understanding of how HTTP methods map to backend operations.

Example:

```text
GET
POST
PUT
PATCH
DELETE
```

We will not immediately hide the implementation behind ViewSets or Generic Views.

Those abstractions can be introduced later for comparison and refactoring.

---

# 12. API Endpoints

The following endpoints are planned.

## Projects

### Create Project

```http
POST /api/projects/
```

Example request:

```json
{
  "name": "TaskFlow",
  "key": "TF",
  "description": "Project management application"
}
```

### Get Projects

```http
GET /api/projects/
```

### Get Project

```http
GET /api/projects/<id>/
```

### Update Project

```http
PUT /api/projects/<id>/
```

or partial update:

```http
PATCH /api/projects/<id>/
```

### Delete Project

```http
DELETE /api/projects/<id>/
```

---

# 13. Sprint APIs

### Create Sprint

```http
POST /api/sprints/
```

### Get Sprints

```http
GET /api/sprints/
```

### Get Sprint

```http
GET /api/sprints/<id>/
```

### Update Sprint

```http
PUT /api/sprints/<id>/
```

or:

```http
PATCH /api/sprints/<id>/
```

### Delete Sprint

```http
DELETE /api/sprints/<id>/
```

---

# 14. Ticket APIs

### Create Ticket

```http
POST /api/tickets/
```

Example:

```json
{
  "title": "Implement Login API",
  "description": "Create login endpoint using DRF",
  "project": 1,
  "priority": "HIGH"
}
```

### Get Tickets

```http
GET /api/tickets/
```

### Get Ticket

```http
GET /api/tickets/<id>/
```

### Complete Ticket Update

```http
PUT /api/tickets/<id>/
```

### Partial Ticket Update

```http
PATCH /api/tickets/<id>/
```

### Delete Ticket

```http
DELETE /api/tickets/<id>/
```

---

# 15. Ticket Assignment

Assign a ticket to a user using a partial update.

```http
PATCH /api/tickets/<id>/
```

Example:

```json
{
  "assignee": 5
}
```

This is preferred over creating a separate endpoint initially because assignment is simply an update to the ticket.

---

# 16. Changing Ticket Status

Ticket status can also be changed using a partial update.

```http
PATCH /api/tickets/<id>/
```

Example:

```json
{
  "status": "IN_PROGRESS"
}
```

Another example:

```json
{
  "status": "DONE"
}
```

The serializer/business logic will eventually validate whether the requested status is valid.

---

# 17. Sprint Assignment

A ticket can be added to a sprint using:

```http
PATCH /api/tickets/<id>/
```

Example:

```json
{
  "sprint": 2
}
```

To move a ticket back to the backlog:

```json
{
  "sprint": null
}
```

---

# 18. Reporter

The reporter represents the user who created/reported the ticket.

Example:

```text
Ticket: TF-101

Reporter:
Asif

Assignee:
Mohamed
```

Reporter and assignee both reference the User model but represent different relationships.

---

# 19. Validation

Validation will be implemented through DRF serializers.

Examples:

### Project

```text
Project name cannot be empty.
Project key cannot be empty.
Project key should be unique.
```

### Sprint

```text
Sprint must belong to a project.
Start date should not be after end date.
```

### Ticket

```text
Title cannot be empty.
Project must exist.
Assignee must exist if provided.
Sprint must exist if provided.
Priority must be valid.
Status must be valid.
```

More business rules can be introduced as development progresses.

---

# 20. Authentication

Authentication will be introduced after the core CRUD APIs are working.

Users should eventually be able to:

```text
Register
Login
Access protected APIs
```

Authenticated users will be associated with actions such as:

```text
Create Ticket
Report Ticket
Assign Ticket
Update Ticket
```

Authentication technology will be decided during implementation based on the learning requirements.

---

# 21. Permissions

Basic permissions will eventually be added.

Initial roles:

```text
ADMIN
MEMBER
```

Potential behavior:

```text
ADMIN
 ├── Manage projects
 ├── Manage users
 ├── Manage sprints
 └── Manage tickets

MEMBER
 ├── View projects
 ├── Create tickets
 ├── Update tickets
 └── Work on assigned tickets
```

Exact permission rules will be finalized during implementation.

---

# 22. Filtering

Tickets should eventually support filtering.

Examples:

```http
GET /api/tickets/?status=TODO
```

```http
GET /api/tickets/?priority=HIGH
```

```http
GET /api/tickets/?assignee=5
```

```http
GET /api/tickets/?sprint=2
```

Multiple filters may also be supported:

```http
GET /api/tickets/?status=IN_PROGRESS&priority=HIGH
```

---

# 23. Search

Ticket search can eventually support:

```http
GET /api/tickets/?search=login
```

Search can be performed against fields such as:

```text
title
description
key
```

---

# 24. Pagination

When the number of tickets increases, the API should return paginated results instead of returning every ticket at once.

Example:

```http
GET /api/tickets/?page=2
```

The exact pagination configuration will be decided during implementation.

---

# 25. Frontend Plan

The frontend will be developed only after the backend is sufficiently complete.

Technology:

```text
React
```

The frontend will consume the Django REST APIs.

Planned screens:

```text
Login
   |
   ↓
Projects
   |
   ├── Project Details
   |
   ├── Backlog
   |
   ├── Sprint
   |
   └── Kanban Board
```

---

# 26. Kanban Board

The main ticket-management UI will eventually look similar to:

```text
┌────────────┬───────────────┬────────────┬──────────┐
│    TODO    │  IN_PROGRESS  │ IN_REVIEW  │   DONE   │
├────────────┼───────────────┼────────────┼──────────┤
│ TF-101     │ TF-104        │ TF-108     │ TF-102   │
│ Login API  │ Auth API      │ UI Review  │ Navbar   │
│            │               │            │          │
│ TF-103     │ TF-105        │            │ TF-106   │
│ Dashboard  │ User API      │            │ Footer   │
└────────────┴───────────────┴────────────┴──────────┘
```

Eventually tickets can be moved between columns using drag-and-drop.

For example:

```text
TODO
 ↓
Drag TF-101
 ↓
IN_PROGRESS
 ↓
PATCH /api/tickets/101/
{
    "status": "IN_PROGRESS"
}
```

---

# 27. Development Sequence

The project will be implemented in the following order.

```text
1. Requirements
      ↓
2. Database Design
      ↓
3. Django Project Setup
      ↓
4. Django Models
      ↓
5. PostgreSQL Connection
      ↓
6. Migrations
      ↓
7. Serializers
      ↓
8. APIViews
      ↓
9. Project CRUD APIs
      ↓
10. Sprint CRUD APIs
      ↓
11. Ticket CRUD APIs
      ↓
12. Relationships
      ↓
13. Validation
      ↓
14. Business Logic
      ↓
15. Authentication
      ↓
16. Permissions
      ↓
17. Filtering
      ↓
18. Search
      ↓
19. Pagination
      ↓
20. API Testing
      ↓
21. React Frontend
      ↓
22. Kanban Board
      ↓
23. Frontend Authentication
      ↓
24. Integration
      ↓
25. Deployment
```

---

# 28. Backend Architecture

The initial backend structure will follow a simple Django application structure.

Expected structure:

```text
taskflow-backend/
│
├── manage.py
│
├── .env
├── .gitignore
├── requirements.txt
│
├── taskflow/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── core/
    ├── migrations/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── tests.py
```

The exact application structure may be split into multiple Django apps if the project grows.

For the initial version, keeping the structure simple is preferred.

---

# 29. API Development Philosophy

The project is also intended as a Django/DRF learning project.

Therefore, implementation should prioritize understanding over abstraction.

Initially:

```text
APIView
    ↓
Serializer
    ↓
Model
    ↓
ORM
    ↓
PostgreSQL
```

After understanding the implementation, selected APIs can be refactored using:

```text
Generic Views
ViewSets
Routers
```

This allows comparison between explicit and abstracted DRF implementations.

---

# 30. Testing

APIs will initially be tested using:

```text
Postman
```

Each API should be tested for:

- Successful requests
- Invalid input
- Missing fields
- Invalid IDs
- Invalid status values
- Invalid relationships
- Unauthorized access
- Permission failures
- Delete operations

Automated Django/DRF tests can be added after the core APIs are stable.

---

# 31. Error Response Format

The API should return consistent JSON responses.

Example success:

```json
{
  "success": true,
  "message": "Ticket created successfully",
  "data": {
    "id": 1,
    "key": "TF-1"
  }
}
```

Example error:

```json
{
  "success": false,
  "message": "Ticket not found"
}
```

Exact response formatting will be standardized during API implementation.

---

# 32. Future Enhancements

The following features are intentionally outside the initial scope but may be added later:

```text
Comments
Attachments
Labels
Ticket history
Notifications
Dashboard analytics
Activity timeline
Advanced permissions
Email notifications
WebSockets / real-time updates
Docker
CI/CD
Cloud deployment
```

These should only be added after the core application is complete.

---

# 33. Initial Scope

The MVP should contain:

```text
✓ Django
✓ Django REST Framework
✓ PostgreSQL
✓ User management
✓ Projects
✓ Sprints
✓ Tickets
✓ Ticket assignment
✓ Ticket reporter
✓ Ticket status
✓ Ticket priority
✓ CRUD APIs
✓ Relationships
✓ Serializer validation
✓ Authentication
✓ Basic permissions
✓ Filtering
✓ Search
✓ Pagination
✓ React frontend
✓ Kanban board
```

The goal is not to reproduce JIRA.

The goal is to build a **small but realistic project management application** while learning how a production-style Django REST backend is structured.

---

# 34. Learning Objectives

By completing TaskFlow, the following concepts should be understood:

### Django

- Project structure
- Applications
- Settings
- URLs
- Models
- Migrations
- Django ORM
- Authentication

### PostgreSQL

- Database connection
- Tables
- Relationships
- Foreign keys
- Querying through Django ORM

### Django REST Framework

- APIView
- Request/Response
- Serializers
- ModelSerializer
- Serializer validation
- CRUD APIs
- Generic Views
- ViewSets
- Routers
- Authentication
- Permissions
- Filtering
- Pagination

### Backend Architecture

```text
Client
  ↓
HTTP Request
  ↓
URL
  ↓
APIView
  ↓
Serializer
  ↓
Validation
  ↓
Django ORM
  ↓
PostgreSQL
  ↓
Django ORM
  ↓
Serializer
  ↓
HTTP Response
  ↓
Client
```

---

# 35. Final Goal

The final application should allow a user to perform the complete basic project-management workflow:

```text
Create Project
       ↓
Create Sprint
       ↓
Create Ticket
       ↓
Assign Ticket
       ↓
Add Ticket to Sprint
       ↓
TODO
       ↓
IN_PROGRESS
       ↓
IN_REVIEW
       ↓
DONE
```

The backend will be built first and thoroughly tested.

The React frontend will then consume the completed REST APIs and provide the visual project-management interface.

---

# 36. Resume Description

After completion, the project can be presented on a resume as:

**TaskFlow — Full-Stack Project Management Platform**

> Built a JIRA-inspired project management platform using React, Django REST Framework, and PostgreSQL, implementing project, sprint, and ticket management with relational data modeling, RESTful CRUD APIs, ticket assignment, status workflows, serializer validation, authentication, filtering, search, pagination, and a Kanban-style interface.

---

# 37. Current Project Status

```text
Requirements        ✓ Completed
Database Design     ✓ Completed
Backend             → To Implement
Frontend            → Later
Deployment          → Later
```

The next implementation step is:

```text
STEP 3
Django Project Setup
```

From this point onward, implementation should follow the architecture and requirements defined in this document.
