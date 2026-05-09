from __future__ import annotations

from dataclasses import dataclass, field
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
