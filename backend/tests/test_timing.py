
import pytest

from backend.timing import find_timing_bursts, parse_timestamp


def test_detects_posts_within_time_window():
    posts = [
        {"id": "1", "account": "user1", "timestamp": "2026-11-14T10:00:00Z"},
        {"id": "2", "account": "user2", "timestamp": "2026-11-14T10:00:20Z"},
        {"id": "3", "account": "user3", "timestamp": "2026-11-14T10:00:40Z"}
    ]

    bursts = find_timing_bursts(
        posts,
        window_seconds=60,
        min_accounts=3
    )

    assert len(bursts) > 0
    assert bursts[0]["account_count"] == 3


def test_does_not_detect_posts_outside_window():
    posts = [
        {"id": "1", "account": "user1", "timestamp": "2026-11-14T10:00:00Z"},
        {"id": "2", "account": "user2", "timestamp": "2026-11-14T10:05:00Z"},
        {"id": "3", "account": "user3", "timestamp": "2026-11-14T10:10:00Z"}
    ]

    bursts = find_timing_bursts(
        posts,
        window_seconds=60,
        min_accounts=3
    )

    assert bursts == []


def test_requires_unique_accounts():
    posts = [
        {"id": "1", "account": "user1", "timestamp": "2026-11-14T10:00:00Z"},
        {"id": "2", "account": "user1", "timestamp": "2026-11-14T10:00:10Z"},
        {"id": "3", "account": "user1", "timestamp": "2026-11-14T10:00:20Z"}
    ]

    assert find_timing_bursts(posts, min_accounts=3) == []


def test_rejects_invalid_timestamp():
    with pytest.raises(ValueError):
        parse_timestamp("not-a-timestamp")
