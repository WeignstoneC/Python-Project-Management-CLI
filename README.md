# Python Project Management CLI

This project provides a small command-line tool for managing users, projects, and tasks with JSON-based persistence.

## Features
- Add and list users
- Add projects for a specific user
- Add tasks to a project and mark them complete
- Persist data locally in a JSON file

## Usage
Run the CLI from the project directory:

```bash
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py add-project --user "Alex" --title "CLI Tool" --description "Build a tool" --due-date "2026-08-01"
python main.py add-task --project "CLI Tool" --title "Implement CLI" --assigned-to "Alex" --contributors "Alex,Jamie"
python main.py complete-task --project "CLI Tool" --title "Implement CLI"
python main.py list-users
python main.py list-projects --user "Alex"
```

## Testing
Run the tests with:

```bash
PYTHONPATH=. pytest -q
```
