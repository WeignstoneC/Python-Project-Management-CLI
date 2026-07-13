import argparse
import json
from pathlib import Path
from typing import List


class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email


class Project:
    def __init__(self, title: str, description: str, due_date: str, user_name: str):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.user_name = user_name


class Task:
    def __init__(self, title: str, status: str, assigned_to: str, contributors: List[str], project_title: str):
        self.title = title
        self.status = status
        self.assigned_to = assigned_to
        self.contributors = contributors
        self.project_title = project_title


class ProjectManager:
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.users: List[User] = []
        self.projects: List[Project] = []
        self.tasks: List[Task] = []
        self.load()

    def load(self) -> None:
        if not self.data_file.exists():
            self.save()
            return

        payload = json.loads(self.data_file.read_text())
        self.users = [User(item["name"], item["email"]) for item in payload.get("users", [])]
        self.projects = [
            Project(item["title"], item["description"], item["due_date"], item["user_name"])
            for item in payload.get("projects", [])
        ]
        self.tasks = [
            Task(
                item["title"],
                item["status"],
                item["assigned_to"],
                item.get("contributors", []),
                item["project_title"],
            )
            for item in payload.get("tasks", [])
        ]

    def save(self) -> None:
        payload = {
            "users": [{"name": user.name, "email": user.email} for user in self.users],
            "projects": [
                {
                    "title": project.title,
                    "description": project.description,
                    "due_date": project.due_date,
                    "user_name": project.user_name,
                }
                for project in self.projects
            ],
            "tasks": [
                {
                    "title": task.title,
                    "status": task.status,
                    "assigned_to": task.assigned_to,
                    "contributors": task.contributors,
                    "project_title": task.project_title,
                }
                for task in self.tasks
            ],
        }
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.data_file.write_text(json.dumps(payload, indent=2))

    def add_user(self, name: str, email: str) -> None:
        self.users.append(User(name, email))
        self.save()

    def add_project(self, user_name: str, title: str, description: str, due_date: str) -> None:
        if not any(user.name == user_name for user in self.users):
            raise ValueError(f"User '{user_name}' does not exist")
        self.projects.append(Project(title, description, due_date, user_name))
        self.save()

    def add_task(self, project_title: str, title: str, assigned_to: str, contributors: List[str]) -> None:
        if not any(project.title == project_title for project in self.projects):
            raise ValueError(f"Project '{project_title}' does not exist")
        clean_contributors = [name.strip() for name in contributors if name and name.strip()]
        self.tasks.append(Task(title, "pending", assigned_to, clean_contributors, project_title))
        self.save()

    def complete_task(self, project_title: str, title: str) -> None:
        for task in self.tasks:
            if task.project_title == project_title and task.title == title:
                task.status = "complete"
                self.save()
                return
        raise ValueError(f"Task '{title}' not found for project '{project_title}'")

    def list_users(self) -> List[User]:
        return self.users

    def list_projects(self, user_name: str | None = None) -> List[Project]:
        if user_name is None:
            return self.projects
        return [project for project in self.projects if project.user_name == user_name]

    def list_tasks(self, project_title: str | None = None) -> List[Task]:
        if project_title is None:
            return self.tasks
        return [task for task in self.tasks if task.project_title == project_title]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_user = subparsers.add_parser("add-user", help="Add a user")
    add_user.add_argument("--name", required=True)
    add_user.add_argument("--email", required=True)

    add_project = subparsers.add_parser("add-project", help="Add a project")
    add_project.add_argument("--user", required=True)
    add_project.add_argument("--title", required=True)
    add_project.add_argument("--description", required=True)
    add_project.add_argument("--due-date", required=True)

    add_task = subparsers.add_parser("add-task", help="Add a task")
    add_task.add_argument("--project", required=True)
    add_task.add_argument("--title", required=True)
    add_task.add_argument("--assigned-to", required=True)
    add_task.add_argument("--contributors", nargs="*", default=[])

    complete_task = subparsers.add_parser("complete-task", help="Mark a task complete")
    complete_task.add_argument("--project", required=True)
    complete_task.add_argument("--title", required=True)

    list_users = subparsers.add_parser("list-users", help="List users")
    list_projects = subparsers.add_parser("list-projects", help="List projects")
    list_projects.add_argument("--user", default=None)

    return parser


def parse_contributors(values: List[str]) -> List[str]:
    parsed: List[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part and part.strip())
    return parsed


def run_cli(args: List[str] | None = None, data_file: Path | None = None) -> None:
    path = data_file or Path(__file__).resolve().parent / "data" / "project_data.json"
    manager = ProjectManager(path)
    parser = build_parser()
    parsed = parser.parse_args(args)

    if parsed.command == "add-user":
        manager.add_user(parsed.name, parsed.email)
        print(f"Added user: {parsed.name}")
    elif parsed.command == "add-project":
        manager.add_project(parsed.user, parsed.title, parsed.description, parsed.due_date)
        print(f"Added project: {parsed.title}")
    elif parsed.command == "add-task":
        contributors = parse_contributors(parsed.contributors)
        manager.add_task(parsed.project, parsed.title, parsed.assigned_to, contributors)
        print(f"Added task: {parsed.title}")
    elif parsed.command == "complete-task":
        manager.complete_task(parsed.project, parsed.title)
        print(f"Completed task: {parsed.title}")
    elif parsed.command == "list-users":
        for user in manager.list_users():
            print(f"{user.name} | {user.email}")
    elif parsed.command == "list-projects":
        for project in manager.list_projects(parsed.user):
            print(f"{project.title} | {project.description} | {project.due_date} | {project.user_name}")


if __name__ == "__main__":
    run_cli()
