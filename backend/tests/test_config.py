from pathlib import Path

from app.core.config import load_settings


def test_load_settings_reads_backend_dotenv_values(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=sk-test",
                "OPENAI_TEXT_MODEL=gpt-test",
                "FFMPEG_BINARY=C:/ffmpeg/bin/ffmpeg.exe",
                "ARTIFACTS_DIR=custom-artifacts",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file, environ={})

    assert settings.openai_api_key == "sk-test"
    assert settings.openai_text_model == "gpt-test"
    assert settings.ffmpeg_binary == "C:/ffmpeg/bin/ffmpeg.exe"
    assert settings.artifacts_dir == Path("custom-artifacts")


def test_load_settings_prefers_environment_over_backend_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-file\n", encoding="utf-8")

    settings = load_settings(
        env_file=env_file,
        environ={"OPENAI_API_KEY": "sk-env", "OPENAI_TEXT_MODEL": "gpt-env"},
    )

    assert settings.openai_api_key == "sk-env"
    assert settings.openai_text_model == "gpt-env"
