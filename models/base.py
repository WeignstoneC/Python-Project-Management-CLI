"""Core domain classes for users, projects, and tasks."""

from __future__ import annotations

from typing import List


class BaseModel:
    """Base class that assigns a simple sequential identifier to each model."""

    _id_counter = 0

    def __init__(self) -> None:
        """Create a model instance with an incrementing identifier."""
        type(self)._id_counter += 1
        self.id = type(self)._id_counter


class Person(BaseModel):
    """Represents a person in the system with a validated name and email."""

    def __init__(self, name: str, email: str | None = None) -> None:
        """Initialize a person with a name and an optional email address."""
        super().__init__()
        self._name = ""
        self._email = ""
        self.name = name
        self.email = email or ""

    @property
    def name(self) -> str:
        """Return the person's current name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Validate and store the person's name."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Return the person's email address."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Store the person's email address."""
        self._email = value.strip()

    def __str__(self) -> str:
        """Return the person's display name."""
        return self.name


class User(Person):
    """Represents a team member who can own multiple projects."""

    def __init__(self, name: str, email: str) -> None:
        """Create a user with an initial project list."""
        super().__init__(name, email)
        self.projects: List["Project"] = []

    def add_project(self, project: "Project") -> None:
        """Attach a project to this user if it is not already present."""
        if project not in self.projects:
            self.projects.append(project)


class Project(BaseModel):
    """Represents a project belonging to a single user."""

    def __init__(self, title: str, description: str, due_date: str, user_name: str) -> None:
        """Initialize a project with title, description, due date, and owner."""
        super().__init__()
        self._title = ""
        self._description = ""
        self._due_date = ""
        self.user_name = user_name
        self.title = title
        self.description = description
        self.due_date = due_date
        self.tasks: List["Task"] = []

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Project title cannot be empty")
        self._title = value.strip()

    @property
    def description(self) -> str:
        """Return the project's description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Store the project's description."""
        self._description = value.strip() if value else ""

    @property
    def due_date(self) -> str:
        """Return the project's due date."""
        return self._due_date

    @due_date.setter
    def due_date(self, value: str) -> None:
        """Store the project's due date."""
        self._due_date = value.strip() if value else ""

    def add_task(self, task: "Task") -> None:
        """Attach a task to this project if it is not already present."""
        if task not in self.tasks:
            self.tasks.append(task)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "user_name": self.user_name,
        }


class Task(BaseModel):
    """Represents a task within a project."""

    def __init__(self, title: str, status: str = "pending", assigned_to: str = "", contributors: List[str] | None = None, project_title: str = "") -> None:
        """Initialize a task with title, status, owner, contributors, and project reference."""
        super().__init__()
        self._title = ""
        self._status = "pending"
        self._assigned_to = assigned_to
        self._contributors: List[str] = []
        self.project_title = project_title
        self.title = title
        self.status = status
        self.contributors = contributors or []

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty")
        self._title = value.strip()

    @property
    def status(self) -> str:
        """Return the task status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        """Validate and store the task status."""
        allowed = {"pending", "complete"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError("Status must be 'pending' or 'complete'")
        self._status = normalized

    @property
    def assigned_to(self) -> str:
        """Return the person assigned to the task."""
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value: str) -> None:
        """Store the assigned person for the task."""
        self._assigned_to = value.strip()

    @property
    def contributors(self) -> List[str]:
        """Return the current contributors attached to the task."""
        return self._contributors

    @contributors.setter
    def contributors(self, values: List[str]) -> None:
        """Normalize the contributor list for storage."""
        self._contributors = [name.strip() for name in values if name and name.strip()]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "contributors": self.contributors,
            "project_title": self.project_title,
        }
