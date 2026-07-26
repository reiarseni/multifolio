from unittest.mock import patch

import pytest

from app.services.media_service import delete_media, validate_video_embed


def test_validate_video_embed_youtube():
    url = "https://www.youtube.com/watch?v=abc123"
    assert validate_video_embed(url) == url


def test_validate_video_embed_youtu_be():
    url = "https://youtu.be/abc123"
    assert validate_video_embed(url) == url


def test_validate_video_embed_vimeo():
    url = "https://vimeo.com/123456"
    assert validate_video_embed(url) == url


def test_validate_video_embed_vimeo_www():
    url = "https://www.vimeo.com/123456"
    assert validate_video_embed(url) == url


def test_validate_video_embed_invalid():
    with pytest.raises(Exception) as exc_info:
        validate_video_embed("https://example.com/video.mp4")
    assert exc_info.value.status_code == 400


def test_delete_media_existing_file(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    test_file = media_dir / "test.webp"
    test_file.write_bytes(b"fake image data")

    with patch("app.services.media_service.settings") as mock_settings:
        mock_settings.media_dir = str(media_dir)
        delete_media("/media/test.webp")

    assert not test_file.exists()


def test_delete_media_nonexistent_file(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()

    with patch("app.services.media_service.settings") as mock_settings:
        mock_settings.media_dir = str(media_dir)
        delete_media("/media/nonexistent.webp")


def test_delete_media_non_media_url():
    delete_media("https://example.com/image.jpg")
