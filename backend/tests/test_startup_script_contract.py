from pathlib import Path


def test_windows_startup_wrapper_invokes_dev_powershell_script() -> None:
    script_path = Path("scripts/start-dev.cmd")

    assert script_path.exists()

    content = script_path.read_text(encoding="utf-8")

    assert "dev.ps1" in content
    assert "powershell" in content.lower()
    assert "Frontend URL:" in content
    assert "Backend URL: http://127.0.0.1:8001" in content


def test_dev_script_uses_fixed_ports_and_clears_port_owners() -> None:
    script_path = Path("scripts/dev.ps1")

    assert script_path.exists()

    content = script_path.read_text(encoding="utf-8")

    assert "[int]$BackendPort = 8001" in content
    assert "[int]$FrontendPort = 3000" in content
    assert "Get-NetTCPConnection -LocalPort $Port -State Listen" in content
    assert "Stop-Process -Id $processId -Force" in content
    assert "NEXT_PUBLIC_API_BASE_URL='http://127.0.0.1:$BackendPort'" in content
    assert content.count('Start-Process -FilePath "powershell"') >= 2
