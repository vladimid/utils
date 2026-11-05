import json

from utils import command_exists, load_config, parse_env_file, shell_quote


def test_shell_quote_handles_spaces():
    assert shell_quote("hello world") == "'hello world'"


def test_command_exists_for_python_executable():
    assert command_exists("python") or command_exists("python3")


def test_parse_env_file_supports_exports_and_quotes(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# comment\n"
        "export APP_NAME='demo app'\n"
        "PORT=8080\n"
        "DEBUG=true\n",
        encoding="utf-8",
    )

    values = parse_env_file(env_path)
    assert values["APP_NAME"] == "demo app"
    assert values["PORT"] == "8080"
    assert values["DEBUG"] == "true"


def test_load_config_accepts_json_and_ini(tmp_path):
    json_path = tmp_path / "settings.json"
    json_path.write_text(json.dumps({"debug": True, "port": 9000}), encoding="utf-8")
    assert load_config(json_path) == {"debug": True, "port": 9000}

    ini_path = tmp_path / "settings.ini"
    ini_path.write_text("[server]\nport = 8080\n", encoding="utf-8")
    assert load_config(ini_path) == {"server": {"port": "8080"}}


def test_cli_quote_output():
    from utils.cli import main

    assert main(["--quote", "hello world"]) == 0
