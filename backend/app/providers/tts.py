from __future__ import annotations

import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

import httpx
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
        speech_path = self._output_dir / "audio" / job_id / "voice.wav"
        speech_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(speech_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(b"\x00\x00" * 24000)
        return TTSResponse(asset_uri=str(speech_path), provider_name=self.provider_name)


class QwenTTSProvider:
    provider_name = "qwen"

    def __init__(self, *, api_key: str, model: str, default_voice: str, output_dir: Path, base_url: str) -> None:
        self._api_key = api_key
        self._model = model
        self._default_voice = default_voice
        self._output_dir = output_dir
        self._base_url = base_url.rstrip("/")
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        voice = request.voice if request.voice != "default" else self._default_voice
        job_id = request.metadata.get("job_id", "adhoc")
        speech_path = self._output_dir / "audio" / job_id / "voice.mp3"
        speech_path.parent.mkdir(parents=True, exist_ok=True)

        response = httpx.post(
            f"{self._base_url}/services/aigc/multimodal-generation/generation",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "false",
            },
            json={
                "model": self._model,
                "input": {"text": request.text, "voice": voice},
                "parameters": {"format": "mp3"},
            },
            timeout=120.0,
        )
        response.raise_for_status()
        payload = response.json()
        audio_url = _extract_qwen_audio_url(payload)
        audio_response = httpx.get(audio_url, timeout=120.0)
        audio_response.raise_for_status()
        speech_path.write_bytes(audio_response.content)
        return TTSResponse(asset_uri=str(speech_path), provider_name=self.provider_name)


def _extract_qwen_audio_url(payload: Mapping[str, object]) -> str:
    output = payload.get("output")
    if not isinstance(output, Mapping):
        raise ValueError("Qwen TTS returned no output payload")

    audio = output.get("audio")
    if isinstance(audio, Mapping):
        audio_url = audio.get("url")
        if isinstance(audio_url, str) and audio_url:
            return audio_url

    audio_url = output.get("audio_url")
    if isinstance(audio_url, str) and audio_url:
        return audio_url

    raise ValueError("Qwen TTS returned no audio URL")
