import json

from main import run_cli


def test_add_user_and_list_users(tmp_path, capsys):
    data_file = tmp_path / "data.json"

    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], data_file=data_file)
    run_cli(["list-users"], data_file=data_file)

    captured = capsys.readouterr().out
    assert "Alex" in captured
    assert "alex@example.com" in captured


def test_add_project_and_list_projects_for_user(tmp_path, capsys):
    data_file = tmp_path / "data.json"

    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], data_file=data_file)
    run_cli(
        [
            "add-project",
            "--user",
            "Alex",
            "--title",
            "CLI Tool",
            "--description",
            "Build a tool",
            "--due-date",
            "2026-08-01",
        ],
        data_file=data_file,
    )
    run_cli(["list-projects", "--user", "Alex"], data_file=data_file)

    captured = capsys.readouterr().out
    assert "CLI Tool" in captured
    assert "Build a tool" in captured


def test_add_task_complete_and_persist(tmp_path):
    data_file = tmp_path / "data.json"

    run_cli(["add-user", "--name", "Alex", "--email", "alex@example.com"], data_file=data_file)
    run_cli(
        [
            "add-project",
            "--user",
            "Alex",
            "--title",
            "CLI Tool",
            "--description",
            "Build a tool",
            "--due-date",
            "2026-08-01",
        ],
        data_file=data_file,
    )
    run_cli(
        [
            "add-task",
            "--project",
            "CLI Tool",
            "--title",
            "Implement CLI",
            "--assigned-to",
            "Alex",
            "--contributors",
            "Alex,Jamie",
        ],
        data_file=data_file,
    )
    run_cli(["complete-task", "--project", "CLI Tool", "--title", "Implement CLI"], data_file=data_file)

    payload = json.loads(data_file.read_text())
    assert payload["tasks"][0]["status"] == "complete"
