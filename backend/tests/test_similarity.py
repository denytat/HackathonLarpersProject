
from backend.similarity import find_similar_posts


def test_identifies_similar_posts():
    posts = [
        {
            "id": "1",
            "account": "user1",
            "text": "Breaking news about a major election today"
        },
        {
            "id": "2",
            "account": "user2",
            "text": "Breaking news about a major election today"
        },
        {
            "id": "3",
            "account": "user3",
            "text": "I enjoy playing football on weekends"
        }
    ]

    matches = find_similar_posts(posts, threshold=0.75)

    assert len(matches) == 1
    assert matches[0]["post_1"] == "1"
    assert matches[0]["post_2"] == "2"


def test_returns_empty_for_single_post():
    posts = [
        {"id": "1", "account": "user1", "text": "Hello world"}
    ]

    assert find_similar_posts(posts) == []


def test_returns_empty_for_identical_empty_texts():
    posts = [
        {"id": "1", "account": "user1", "text": ""},
        {"id": "2", "account": "user2", "text": ""}
    ]

    assert find_similar_posts(posts) == []
