import json

from main import run_cli



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


def test_edit_project_due_date(tmp_path):
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

    run_cli(["edit-project", "--project", "CLI Tool", "--due-date", "2026-09-15"], data_file=data_file)

    payload = json.loads(data_file.read_text())
    assert payload["projects"][0]["due_date"] == "2026-09-15"


def test_edit_project_and_list_tasks(tmp_path, capsys):
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
            "Alex",
        ],
        data_file=data_file,
    )
    run_cli(["edit-project", "--project", "CLI Tool", "--description", "Refined scope"], data_file=data_file)
    run_cli(["list-tasks", "--project", "CLI Tool"], data_file=data_file)

    captured = capsys.readouterr().out
    assert "Refined scope" in captured
    assert "Implement CLI" in captured
