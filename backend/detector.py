from backend.similarity import find_similar_posts
from backend.timing import find_timing_bursts
from backend.account_similarity import find_similar_accounts
from backend.clustering import detect_swarms


def analyze_posts(posts):
    """
    Detect coordinated activity and produce preliminary post verdicts.

    Organic means no coordination was detected.
    Uncertain means the post belongs to a detected coordinated group.
    Coordination alone does not establish malicious intent.
    """
    posts = [
        post.model_dump() if hasattr(post, "model_dump") else post
        for post in posts
    ]

    text_matches = find_similar_posts(
        posts,
        threshold=0.75,
    )

    timing_bursts = find_timing_bursts(
        posts,
        window_seconds=60,
        min_accounts=3,
    )

    profiles, account_matches = find_similar_accounts(
        posts,
        threshold=0.75,
        min_posts=2,
    )

    swarms = detect_swarms(
        text_matches,
        timing_bursts,
        account_matches,
        min_signals=2,
        min_accounts=3,
    )

    account_signals = {}
    swarm_accounts = set()

    for swarm in swarms:
        for account in swarm["accounts"]:
            swarm_accounts.add(account)
            account_signals.setdefault(account, set())

        for edge in swarm["evidence"]:
            for account in (
                edge["account_1"],
                edge["account_2"],
            ):
                account_signals.setdefault(account, set())
                account_signals[account].update(
                    edge["signals"].keys()
                )

    signal_names = {
        "text_similarity": "text_similarity",
        "timing_burst": "timing",
        "account_similarity": "account_similarity",
    }

    post_results = []

    for post in posts:
        account = post["account"]
        signals = account_signals.get(account, set())

        detection_signals = sorted(
            signal_names[signal]
            for signal in signals
            if signal in signal_names
        )

        account_scores = [
            swarm["score"]
            for swarm in swarms
            if account in swarm["accounts"]
        ]

        coordination_score = max(account_scores, default=0.0)

        post_results.append({
            "id": post["id"],
            "techniques": [],
            "verdict": (
                "uncertain"
                if account in swarm_accounts
                else "organic"
            ),
            "confidence": coordination_score,
            "flagged_by": detection_signals,
        })

    return {
        "swarms": swarms,
        "posts": post_results,
    }
