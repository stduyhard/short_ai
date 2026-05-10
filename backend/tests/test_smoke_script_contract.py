from pathlib import Path


def test_qwen_smoke_script_contains_expected_runtime_flow() -> None:
    script_path = Path("scripts/run-qwen-smoke.ps1")

    assert script_path.exists()

    content = script_path.read_text(encoding="utf-8")

    assert "/api/runtime/readiness" in content
    assert "/api/jobs" in content
    assert "/run" in content
    assert "Invoke-RestMethod" in content
    assert "voice" in content
    assert "topic" in content
    assert "style" in content
