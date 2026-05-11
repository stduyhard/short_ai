from app.services.storyboard_parser import build_storyboard_shots


def test_build_storyboard_shots_extracts_visual_and_caption_per_section() -> None:
    raw = """
    **分镜①｜0-6s**
    *画面*：特写一只手合上笔记本，阳光落在纸页边缘。
    *字幕*：你合上笔记本的手，比奖状更接近成长。

    **分镜②｜6-12s**
    *画面*：窗边端起咖啡，电脑屏幕上是未保存的文档。
    *字幕*：把一口气，呼得久一点。
    """

    shots = build_storyboard_shots(raw, 2)

    assert shots == [
        {
            "shot": "1",
            "caption": "你合上笔记本的手，比奖状更接近成长。",
            "visual": "特写一只手合上笔记本，阳光落在纸页边缘。",
        },
        {
            "shot": "2",
            "caption": "把一口气，呼得久一点。",
            "visual": "窗边端起咖啡，电脑屏幕上是未保存的文档。",
        },
    ]


def test_build_storyboard_shots_falls_back_when_sections_are_missing() -> None:
    raw = "stub::storyboard::把这段文案拆成 5 个简化分镜"

    shots = build_storyboard_shots(raw, 3)

    assert len(shots) == 3
    assert shots[0]["shot"] == "1"
    assert shots[0]["caption"] == "stub::storyboard::把这段文案拆成 5 个简化分镜"
    assert shots[0]["visual"] == "stub::storyboard::把这段文案拆成 5 个简化分镜"
