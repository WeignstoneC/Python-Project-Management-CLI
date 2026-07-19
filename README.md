# Python Project Management CLI

This project provides a small, modular command-line tool for managing users, projects, and tasks with JSON-based persistence.

## Features
- Create and list users
- Create projects for a specific user
- Assign tasks to projects and mark them complete
- Edit project details and inspect tasks by project
- Persist data locally in a JSON file
- Use the optional Rich package for nicer CLI tables when available

## Project Structure
- main.py: CLI entry point and command parsing
- models/base.py: User, Project, and Task classes with simple OOP behavior
- utils/storage.py: Persistence and relationship management
- data/project_data.json: Local JSON storage file
- tests/test_cli.py: Unit tests for the CLI workflow

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
Run the CLI from the project directory:

```bash
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a tool" --due-date "2026-08-01"
python main.py add-task --project "CLI Tool" --title "Implement CLI" --assigned-to "Alex" --contributors "Alex,Jamie"
python main.py complete-task --project "CLI Tool" --title "Implement CLI"
python main.py edit-project --project "CLI Tool" --description "Refined scope"
python main.py list-users
python main.py list-projects --user "Alex"
python main.py list-tasks --project "CLI Tool"
```

## Testing
Run the tests with:

```bash
PYTHONPATH=. pytest -q
```

## Notes
- The tool stores data in JSON under the data folder.
- If the Rich package is not installed, the CLI falls back to plain text output.

## Known Issues
- Data is stored in a single local JSON file, so there is no multi-user network sync or concurrency control.
- The CLI does not include authentication or role-based permissions yet.
