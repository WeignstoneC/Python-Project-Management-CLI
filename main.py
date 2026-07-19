import argparse
from pathlib import Path
from typing import List, Optional

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:  # pragma: no cover - optional dependency fallback
    Console = None
    Table = None

from utils.storage import ProjectManager


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with subcommands for users, projects, and tasks."""
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

    edit_project = subparsers.add_parser("edit-project", help="Edit a project's description or due date")
    edit_project.add_argument("--project", required=True)
    edit_project.add_argument("--title", default=None)
    edit_project.add_argument("--description", default=None)
    edit_project.add_argument("--due-date", default=None)

    list_users = subparsers.add_parser("list-users", help="List users")
    list_projects = subparsers.add_parser("list-projects", help="List projects")
    list_projects.add_argument("--user", default=None)

    list_tasks = subparsers.add_parser("list-tasks", help="List tasks for a project")
    list_tasks.add_argument("--project", required=True)

    return parser


def parse_contributors(values: List[str]) -> List[str]:
    """Convert contributor input from CLI arguments into a cleaned list of names."""
    parsed: List[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part and part.strip())
    return parsed


def _render_table(rows: List[tuple], headers: List[str]) -> None:
    """Render a list of rows as a simple text table or a Rich table when available."""
    if Console is None or Table is None:
        for row in rows:
            print(" | ".join(row))
        return

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def run_cli(args: Optional[List[str]] = None, data_file: Optional[Path] = None) -> None:
    """Run the CLI for the provided arguments and optional data file path."""
    path = data_file or Path(__file__).resolve().parent / "data" / "project_data.json"
    manager = ProjectManager(path)
    parser = build_parser()
    parsed = parser.parse_args(args)

    try:
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
        elif parsed.command == "edit-project":
            project = manager.edit_project(
                parsed.project,
                description=parsed.description,
                due_date=parsed.due_date,
                title=parsed.title,
            )
            print(f"Updated project: {project.title}")
        elif parsed.command == "list-users":
            rows = [(user.name, user.email) for user in manager.list_users()]
            _render_table(rows, ["Name", "Email"])
        elif parsed.command == "list-projects":
            rows = [(project.title, project.description, project.due_date, project.user_name) for project in manager.list_projects(parsed.user)]
            _render_table(rows, ["Title", "Description", "Due Date", "Owner"])
        elif parsed.command == "list-tasks":
            project = manager.get_project(parsed.project)
            if project is not None:
                print(f"Project: {project.title} | {project.description}")
            rows = [(task.title, task.status, task.assigned_to, ", ".join(task.contributors)) for task in manager.list_tasks(parsed.project)]
            _render_table(rows, ["Title", "Status", "Assigned To", "Contributors"])
        else:
            raise ValueError("Unknown command")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    run_cli()
