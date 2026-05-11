from __future__ import annotations

import re


_SECTION_PATTERN = re.compile(r"(?:\*\*)?分镜\s*([0-9①②③④⑤⑥⑦⑧⑨⑩一二三四五六七八九十]+)[^\n]*")
_MARKDOWN_PATTERN = re.compile(r"[*_`>#]")


def build_storyboard_shots(raw_text: str, shot_count: int) -> list[dict[str, str]]:
    matches = list(_SECTION_PATTERN.finditer(raw_text))
    if not matches:
        return _build_fallback_shots(raw_text, shot_count)

    shots: list[dict[str, str]] = []
    for index, match in enumerate(matches[:shot_count]):
        section_start = match.end()
        section_end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_text)
        section = raw_text[section_start:section_end]
        visual = _extract_labeled_value(section, "画面")
        subtitle = _extract_labeled_value(section, "字幕")
        caption = subtitle or visual or _condense_text(section)
        shots.append(
            {
                "shot": str(index + 1),
                "caption": caption,
                "visual": visual or caption,
            }
        )

    if len(shots) < shot_count:
        last_caption = shots[-1]["caption"] if shots else _condense_text(raw_text)
        last_visual = shots[-1]["visual"] if shots else last_caption
        for index in range(len(shots), shot_count):
            shots.append(
                {
                    "shot": str(index + 1),
                    "caption": last_caption,
                    "visual": last_visual,
                }
            )

    return shots


def _build_fallback_shots(raw_text: str, shot_count: int) -> list[dict[str, str]]:
    condensed = _condense_text(raw_text)
    return [
        {
            "shot": str(index + 1),
            "caption": condensed,
            "visual": condensed,
        }
        for index in range(shot_count)
    ]


def _extract_labeled_value(section: str, label: str) -> str:
    pattern = re.compile(rf"{label}[：:]\s*(.+)")
    for line in section.splitlines():
        stripped = _MARKDOWN_PATTERN.sub("", line).strip()
        if not stripped:
            continue
        match = pattern.search(stripped)
        if match:
            return _condense_text(match.group(1))
    return ""


def _condense_text(text: str) -> str:
    cleaned = _MARKDOWN_PATTERN.sub("", text)
    cleaned = cleaned.replace("✅", "").replace("✨", "").replace("🌱", "")
    cleaned = cleaned.replace("｜", " ").replace("—", " ").replace("–", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned[:220] if len(cleaned) > 220 else cleaned
