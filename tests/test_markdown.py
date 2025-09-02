import pytest
from nodepad.markdown import Video


def test_video_basic_initialization():
    video = Video("https://example.com/test")
    assert video.url == "https://example.com/test"
    assert video.caption == ""


def test_video_initialization_with_caption():
    video = Video("https://example.com/test", "Test Caption")
    assert video.url == "https://example.com/test"
    assert video.caption == "Test Caption"


def test_video_as_markdown_empty_url():
    video = Video("")
    assert video.as_markdown() == "![]()"
    
    video = Video(None)
    assert video.as_markdown() == "![]()"


def test_video_as_markdown_with_mp4_url():
    video = Video("https://example.com/test.mp4")
    assert video.as_markdown() == "![](https://example.com/test.mp4)"


def test_video_as_markdown_with_caption():
    video = Video("https://example.com/test", "My Caption")
    expected = "![My Caption](https://example.com/test.mp4)"
    assert video.as_markdown() == expected


def test_video_format_url_mp4():
    video = Video("https://example.com/test.mp4")
    assert video.format_url() == "https://example.com/test.mp4"


def test_video_format_url_non_mp4():
    video = Video("https://example.com/test")
    assert video.format_url() == "https://example.com/test.mp4"


def test_video_format_url_empty():
    video = Video("")
    assert video.format_url() == ".mp4"