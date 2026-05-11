from __future__ import annotations

import re


_DROP_LINE_PATTERNS = [
    re.compile(r"^\s*[-*#]+\s*"),
    re.compile(r"^\s*说明[:：]?\s*$"),
    re.compile(r"^\s*如需"),
    re.compile(r"^\s*文案特点说明"),
    re.compile(r"^\s*【.*文案.*】\s*$"),
    re.compile(r"^\s*---+\s*$"),
    re.compile(r"^\s*[（(]\s*\d+\s*[-–~]\s*\d+\s*s?.*[）)].*$"),
]


def normalize_script_output(raw_text: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        line = re.sub(r"[*_`]+", "", line).strip()
        if not line:
            continue

        if any(pattern.search(line) for pattern in _DROP_LINE_PATTERNS):
            continue

        line = re.sub(r"^[-*•]\s*", "", line).strip()
        if not line:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
