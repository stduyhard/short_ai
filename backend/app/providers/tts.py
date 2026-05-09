from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

from openai import OpenAI


@dataclass(slots=True, frozen=True)
class TTSRequest:
    text: str
    voice: str = "default"
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TTSResponse:
    asset_uri: str
    provider_name: str


class TTSProvider(Protocol):
    provider_name: str

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        """Return a reference to a synthesized voice asset."""


class OpenAITTSProvider:
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str, default_voice: str, output_dir: Path) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._default_voice = default_voice
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        voice = request.voice if request.voice != "default" else self._default_voice
        job_id = request.metadata.get("job_id", "adhoc")
        speech_path = self._output_dir / "audio" / job_id / "voice.mp3"
        speech_path.parent.mkdir(parents=True, exist_ok=True)

        with self._client.audio.speech.with_streaming_response.create(
            model=self._model,
            voice=voice,
            input=request.text,
        ) as response:
            response.stream_to_file(speech_path)

        return TTSResponse(asset_uri=str(speech_path), provider_name=self.provider_name)


class StubTTSProvider:
    provider_name = "stub"

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        job_id = request.metadata.get("job_id", "adhoc")
        speech_path = self._output_dir / "audio" / job_id / "voice.mp3"
        speech_path.parent.mkdir(parents=True, exist_ok=True)
        speech_path.write_bytes(b"stub-mp3")
        return TTSResponse(asset_uri=str(speech_path), provider_name=self.provider_name)
