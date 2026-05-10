from pathlib import Path


def test_windows_startup_wrapper_invokes_dev_powershell_script() -> None:
    script_path = Path("scripts/start-dev.cmd")

    assert script_path.exists()

    content = script_path.read_text(encoding="utf-8")

    assert "dev.ps1" in content
    assert "powershell" in content.lower()
    assert "Frontend URL:" in content
