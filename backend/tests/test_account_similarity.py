
from backend.account_similarity import find_similar_accounts


def test_detects_similar_account_behaviour():
    posts = []

    for i in range(4):
        posts.append({
            "id": f"a{i}",
            "account": "account_A",
            "text": f"Post A{i}",
            "timestamp": f"2026-11-14T09:{i * 10:02d}:00Z"
        })

        posts.append({
            "id": f"b{i}",
            "account": "account_B",
            "text": f"Post B{i}",
            "timestamp": f"2026-11-14T09:{i * 10 + 2:02d}:00Z"
        })

    profiles, matches = find_similar_accounts(
        posts,
        threshold=0.75,
        min_posts=2
    )

    assert "account_A" in profiles
    assert "account_B" in profiles
    assert len(matches) == 1
    assert matches[0]["similarity"] >= 0.75


def test_ignores_accounts_with_too_few_posts():
    posts = [
        {
            "id": "1",
            "account": "user1",
            "text": "Hello",
            "timestamp": "2026-11-14T10:00:00Z"
        }
    ]

    profiles, matches = find_similar_accounts(
        posts,
        min_posts=2
    )

    assert profiles == {}
    assert matches == []
