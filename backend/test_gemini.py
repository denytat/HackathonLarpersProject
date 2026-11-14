import json

from backend.services.gemini import analyze_swarm


def main():
    swarm = {
        "id": "swarm_1",
        "accounts": ["account_a", "account_b", "account_c"],
        "score": 0.85,
        "evidence": [
            "Similar messages",
            "Posts published within a short time window",
        ],
    }

    posts = [
        {
            "id": "post_1",
            "account": "account_a",
            "text": "Everyone must share this story immediately!",
            "timestamp": "2026-11-14T10:00:00Z",
        },
        {
            "id": "post_2",
            "account": "account_b",
            "text": "Share this story now! Everyone needs to see it!",
            "timestamp": "2026-11-14T10:01:00Z",
        },
        {
            "id": "post_3",
            "account": "account_c",
            "text": "This story must be shared immediately!",
            "timestamp": "2026-11-14T10:02:00Z",
        },
    ]

    result = analyze_swarm(swarm, posts)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()