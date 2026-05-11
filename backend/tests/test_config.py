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
    assert settings.llm_model == "gpt-test"
    assert settings.llm_provider == "openai"
    assert settings.ffmpeg_binary == "C:/ffmpeg/bin/ffmpeg.exe"
    assert settings.artifacts_dir == (tmp_path.parent / "custom-artifacts").resolve()


def test_load_settings_prefers_environment_over_backend_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=sk-file\n", encoding="utf-8")

    settings = load_settings(
        env_file=env_file,
        environ={"OPENAI_API_KEY": "sk-env", "OPENAI_TEXT_MODEL": "gpt-env"},
    )

    assert settings.openai_api_key == "sk-env"
    assert settings.llm_model == "gpt-env"


def test_load_settings_supports_provider_and_dashscope_configuration(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LLM_PROVIDER=qwen",
                "IMAGE_PROVIDER=qwen",
                "TTS_PROVIDER=qwen",
                "VIDEO_PROVIDER=qwen",
                "LLM_MODEL=qwen-plus-latest",
                "IMAGE_MODEL=qwen-image-2.0",
                "TTS_MODEL=qwen3-tts-flash",
                "VIDEO_MODEL=wan2.6-i2v-flash",
                "DASHSCOPE_API_KEY=dash-key",
                "DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file, environ={})

    assert settings.llm_provider == "qwen"
    assert settings.image_provider == "qwen"
    assert settings.tts_provider == "qwen"
    assert settings.video_provider == "qwen"
    assert settings.llm_model == "qwen-plus-latest"
    assert settings.image_model == "qwen-image-2.0"
    assert settings.tts_model == "qwen3-tts-flash"
    assert settings.video_model == "wan2.6-i2v-flash"
    assert settings.dashscope_api_key == "dash-key"
    assert settings.dashscope_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"


def test_load_settings_supports_langsmith_configuration(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "LANGSMITH_TRACING=true",
                "LANGSMITH_API_KEY=ls-key",
                "LANGSMITH_PROJECT=short-video-dev",
                "LANGSMITH_ENDPOINT=https://api.smith.langchain.com",
                "LANGSMITH_WORKSPACE_ID=workspace-123",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file, environ={})

    assert settings.langsmith_tracing is True
    assert settings.langsmith_api_key == "ls-key"
    assert settings.langsmith_project == "short-video-dev"
    assert settings.langsmith_endpoint == "https://api.smith.langchain.com"
    assert settings.langsmith_workspace_id == "workspace-123"


def test_load_settings_discovers_ffmpeg_from_winget_package_directory(tmp_path: Path) -> None:
    local_appdata = tmp_path / "localappdata"
    ffmpeg_path = (
        local_appdata
        / "Microsoft"
        / "WinGet"
        / "Packages"
        / "Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe"
        / "ffmpeg-8.1.1-essentials_build"
        / "bin"
        / "ffmpeg.exe"
    )
    ffmpeg_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_path.write_text("", encoding="utf-8")

    settings = load_settings(
        env_file=tmp_path / ".missing.env",
        environ={"LOCALAPPDATA": str(local_appdata)},
    )

    assert settings.ffmpeg_binary == str(ffmpeg_path)


def test_load_settings_keeps_absolute_artifacts_dir(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("ARTIFACTS_DIR=D:/short_video/artifacts\n", encoding="utf-8")

    settings = load_settings(env_file=env_file, environ={})

    assert settings.artifacts_dir == Path("D:/short_video/artifacts")
