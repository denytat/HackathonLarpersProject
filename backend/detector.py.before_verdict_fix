
from backend.similarity import find_similar_posts
from backend.timing import find_timing_bursts
from backend.account_similarity import find_similar_accounts
from backend.clustering import detect_swarms


def analyze_posts(posts):
    """
    Run all Python-based swarm detection modules.

    Returns potential swarms and preliminary post-level results.
    LLM classification is not implemented yet.
    """

    # Convert Pydantic objects into dictionaries if necessary
    posts = [
        post.model_dump() if hasattr(post, "model_dump") else post
        for post in posts
    ]

    # 1. Text similarity
    text_matches = find_similar_posts(
        posts,
        threshold=0.75
    )

    # 2. Timing bursts
    timing_bursts = find_timing_bursts(
        posts,
        window_seconds=60,
        min_accounts=3
    )

    # 3. Account behaviour
    profiles, account_matches = find_similar_accounts(
        posts,
        threshold=0.75,
        min_posts=2
    )

    # 4. Graph clustering
    swarms = detect_swarms(
        text_matches,
        timing_bursts,
        account_matches,
        min_signals=2,
        min_accounts=3
    )

    # 5. Collect the evidence associated with each account
    account_signals = {}

    for swarm in swarms:
        for account in swarm["accounts"]:
            account_signals.setdefault(account, set())

        for edge in swarm["evidence"]:
            for account in (
                edge["account_1"],
                edge["account_2"]
            ):
                account_signals.setdefault(account, set())
                account_signals[account].update(
                    edge["signals"].keys()
                )

    # 6. Build post-level results
    post_results = []

    signal_names = {
        "text_similarity": "text_similarity",
        "timing_burst": "timing",
        "account_similarity": "account_similarity"
    }

    for post in posts:
        signals = account_signals.get(
            post["account"],
            set()
        )

        flagged_by = sorted(
            signal_names[signal]
            for signal in signals
            if signal in signal_names
        )

        # Find the strongest swarm score for this account
        account_scores = [
            swarm["score"]
            for swarm in swarms
            if post["account"] in swarm["accounts"]
        ]

        evidence_score = max(account_scores, default=0.0)

        post_results.append({
            "id": post["id"],
            "techniques": [],
            "verdict": "uncertain",
            "confidence": evidence_score,
            "flagged_by": flagged_by
        })

    return {
        "swarms": swarms,
        "posts": post_results
    }
