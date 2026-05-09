from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol


@dataclass(slots=True, frozen=True)
class StorageObject:
    path: str
    content_type: str
    metadata: Mapping[str, str] = field(default_factory=dict)


class StorageProvider(Protocol):
    provider_name: str

    def save_text(
        self,
        *,
        path: str,
        content: str,
        content_type: str = "text/plain",
        metadata: Mapping[str, str] | None = None,
    ) -> StorageObject:
        """Persist a text artifact and return its storage descriptor."""

    def save_bytes(
        self,
        *,
        path: str,
        content: bytes,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> StorageObject:
        """Persist a binary artifact and return its storage descriptor."""


class LocalStorageProvider:
    provider_name = "local"

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save_text(
        self,
        *,
        path: str,
        content: str,
        content_type: str = "text/plain",
        metadata: Mapping[str, str] | None = None,
    ) -> StorageObject:
        target = self._resolve(path)
        target.write_text(content, encoding="utf-8")
        return StorageObject(path=str(target), content_type=content_type, metadata=metadata or {})

    def save_bytes(
        self,
        *,
        path: str,
        content: bytes,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> StorageObject:
        target = self._resolve(path)
        target.write_bytes(content)
        return StorageObject(path=str(target), content_type=content_type, metadata=metadata or {})

    def _resolve(self, path: str) -> Path:
        target = self._base_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        return target
