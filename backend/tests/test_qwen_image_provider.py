from __future__ import annotations

from types import SimpleNamespace

from app.providers.image import ImageRequest, QwenImageProvider
from app.providers.storage import LocalStorageProvider


class _FakeResponse:
    def __init__(self, payload: dict[str, object], content: bytes = b"", headers: dict[str, str] | None = None) -> None:
        self._payload = payload
        self.content = content
        self.headers = headers or {"content-type": "image/png"}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


def test_qwen_image_provider_uses_multimodal_generation_for_qwen_image_2_models(
    monkeypatch,
    tmp_path,
) -> None:
    calls: list[SimpleNamespace] = []

    def fake_post(url: str, *, headers: dict[str, str], json: dict[str, object], timeout: float):
        calls.append(SimpleNamespace(url=url, headers=headers, json=json, timeout=timeout))
        return _FakeResponse(
            {
                "output": {
                    "choices": [
                        {
                            "message": {
                                "content": [
                                    {
                                        "image": "https://example.com/generated.png?Expires=123&Signature=abc",
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        )

    def fake_get(url: str, *, timeout: float):
        assert url == "https://example.com/generated.png?Expires=123&Signature=abc"
        return _FakeResponse({}, content=b"png-bytes")

    monkeypatch.setattr("app.providers.image.httpx.post", fake_post)
    monkeypatch.setattr("app.providers.image.httpx.get", fake_get)

    provider = QwenImageProvider(
        api_key="dash-key",
        model="qwen-image-2.0",
        base_url="https://dashscope.aliyuncs.com/api/v1",
        storage_provider=LocalStorageProvider(tmp_path),
    )

    response = provider.generate(
        ImageRequest(
            prompt="为短视频分镜生成竖屏视觉素材：治愈感职场成长插画",
            metadata={"job_id": "job-123"},
        )
    )

    assert calls[0].url == "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    assert calls[0].json["input"] == {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "为短视频分镜生成竖屏视觉素材：治愈感职场成长插画",
                    }
                ],
            }
        ]
    }
    assert calls[0].json["parameters"] == {"size": "1024*1024"}
    assert response.provider_name == "qwen"
    assert response.asset_uri.endswith("generated.png")
    assert "?" not in response.asset_uri
