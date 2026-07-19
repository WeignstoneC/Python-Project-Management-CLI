"""Persistence helpers for storing project data as JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from models.base import Project, Task, User


class ProjectManager:
    """Manage users, projects, and tasks with JSON-based persistence."""

    def __init__(self, data_file: Path):
        """Initialize the manager and load persisted data from disk."""
        self.data_file = data_file
        self.users: List[User] = []
        self.projects: List[Project] = []
        self.tasks: List[Task] = []
        self.load()

    def load(self) -> None:
        """Load users, projects, and tasks from the JSON file, if present."""
        if not self.data_file.exists():
            self.save()
            return

        try:
            payload = json.loads(self.data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            payload = {"users": [], "projects": [], "tasks": []}

        self.users = [User(item["name"], item.get("email", "")) for item in payload.get("users", [])]
        self.projects = [
            Project(item["title"], item.get("description", ""), item.get("due_date", ""), item.get("user_name", ""))
            for item in payload.get("projects", [])
        ]
        self.tasks = [
            Task(
                item["title"],
                item.get("status", "pending"),
                item.get("assigned_to", ""),
                item.get("contributors", []),
                item.get("project_title", ""),
            )
            for item in payload.get("tasks", [])
        ]
        self._rebuild_relationships()

    def save(self) -> None:
        """Persist the current in-memory data to the JSON file."""
        payload = {
            "users": [{"name": user.name, "email": user.email} for user in self.users],
            "projects": [project.to_dict() for project in self.projects],
            "tasks": [task.to_dict() for task in self.tasks],
        }
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.data_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _rebuild_relationships(self) -> None:
        """Reattach projects to users and tasks to projects after loading data."""
        for project in self.projects:
            user = self.get_user(project.user_name)
            if user is not None:
                user.add_project(project)
        for task in self.tasks:
            project = self.get_project(task.project_title)
            if project is not None:
                project.add_task(task)

    def add_user(self, name: str, email: str) -> None:
        """Create a new user and save it to storage."""
        if self.get_user(name) is not None:
            raise ValueError(f"User '{name}' already exists")
        self.users.append(User(name, email))
        self.save()

    def add_project(self, user_name: str, title: str, description: str, due_date: str) -> None:
        """Add a project for an existing user and save it to storage."""
        if self.get_user(user_name) is None:
            raise ValueError(f"User '{user_name}' does not exist")
        if self.get_project(title) is not None:
            raise ValueError(f"Project '{title}' already exists")
        project = Project(title, description, due_date, user_name)
        self.projects.append(project)
        self.get_user(user_name).add_project(project)
        self.save()

    def add_task(self, project_title: str, title: str, assigned_to: str, contributors: List[str]) -> None:
        """Create a task for an existing project and save it to storage."""
        project = self.get_project(project_title)
        if project is None:
            raise ValueError(f"Project '{project_title}' does not exist")
        task = Task(title, "pending", assigned_to, contributors, project_title)
        self.tasks.append(task)
        project.add_task(task)
        self.save()

    def complete_task(self, project_title: str, title: str) -> None:
        """Mark an existing task as complete and save the change."""
        task = self.get_task(project_title, title)
        if task is None:
            raise ValueError(f"Task '{title}' not found for project '{project_title}'")
        task.status = "complete"
        self.save()

    def edit_project(self, project_title: str, description: Optional[str] = None, due_date: Optional[str] = None, title: Optional[str] = None) -> Project:
        """Update a project's title, description, or due date and save the result."""
        project = self.get_project(project_title)
        if project is None:
            raise ValueError(f"Project '{project_title}' does not exist")
        if title is not None:
            if self.get_project(title) is not None and title != project_title:
                raise ValueError(f"Project '{title}' already exists")
            project.title = title
        if description is not None:
            project.description = description
        if due_date is not None:
            project.due_date = due_date
        self.save()
        return project

    def list_users(self) -> List[User]:
        """Return a copy of the registered users."""
        return list(self.users)

    def list_projects(self, user_name: Optional[str] = None) -> List[Project]:
        """Return all projects or only those owned by a specific user."""
        if user_name is None:
            return list(self.projects)
        return [project for project in self.projects if project.user_name == user_name]

    def list_tasks(self, project_title: Optional[str] = None) -> List[Task]:
        """Return all tasks or only those belonging to a specific project."""
        if project_title is None:
            return list(self.tasks)
        return [task for task in self.tasks if task.project_title == project_title]

    def get_user(self, name: str) -> Optional[User]:
        """Look up a user by name."""
        return next((user for user in self.users if user.name == name), None)

    def get_project(self, title: str) -> Optional[Project]:
        """Look up a project by title."""
        return next((project for project in self.projects if project.title == title), None)

    def get_task(self, project_title: str, title: str) -> Optional[Task]:
        """Look up a task by project title and task title."""
        return next((task for task in self.tasks if task.project_title == project_title and task.title == title), None)
