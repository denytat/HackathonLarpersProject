
from collections import Counter
from datetime import datetime
from math import exp, log, sqrt


def parse_timestamp(value):
    timestamp = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    return timestamp


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = sqrt(sum(a * a for a in vector_a))
    magnitude_b = sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def build_account_profiles(posts, min_posts=2):
    """
    Build a posting behaviour profile for each account.

    Accounts need at least min_posts to be included.
    """

    account_posts = {}

    for post in posts:
        account = post["account"]
        account_posts.setdefault(account, []).append(post)

    profiles = {}

    for account, account_items in account_posts.items():

        if len(account_items) < min_posts:
            continue

        timestamps = sorted(
            parse_timestamp(post["timestamp"])
            for post in account_items
        )

        # Calculate time between consecutive posts
        intervals = [
            (timestamps[i] - timestamps[i - 1]).total_seconds()
            for i in range(1, len(timestamps))
        ]

        average_interval = sum(intervals) / len(intervals)

        # Count posts by hour of day (UTC if timestamps are UTC)
        hour_counts = Counter(
            timestamp.hour for timestamp in timestamps
        )

        hour_vector = [
            hour_counts.get(hour, 0)
            for hour in range(24)
        ]

        profiles[account] = {
            "post_count": len(account_items),
            "average_interval_seconds": average_interval,
            "active_hours": hour_vector
        }

    return profiles


def compare_accounts(profile_a, profile_b):
    """Compare two account behaviour profiles."""

    # Similarity of hours in which accounts post
    hours_score = cosine_similarity(
        profile_a["active_hours"],
        profile_b["active_hours"]
    )

    # Similarity of average time between posts
    interval_a = profile_a["average_interval_seconds"]
    interval_b = profile_b["average_interval_seconds"]

    interval_score = exp(
        -abs(log((interval_a + 1) / (interval_b + 1)))
    )

    # Similarity of posting volume
    count_a = profile_a["post_count"]
    count_b = profile_b["post_count"]

    volume_score = min(count_a, count_b) / max(count_a, count_b)

    # Weighted combined score
    total_score = (
        0.50 * hours_score +
        0.30 * interval_score +
        0.20 * volume_score
    )

    return round(total_score, 3)


def find_similar_accounts(posts, threshold=0.75, min_posts=2):
    """Find pairs of accounts with similar posting behaviour."""

    profiles = build_account_profiles(posts, min_posts)

    accounts = list(profiles.keys())
    matches = []

    for i in range(len(accounts)):
        for j in range(i + 1, len(accounts)):

            account_a = accounts[i]
            account_b = accounts[j]

            score = compare_accounts(
                profiles[account_a],
                profiles[account_b]
            )

            if score >= threshold:
                matches.append({
                    "account_1": account_a,
                    "account_2": account_b,
                    "similarity": score,
                    "account_1_posts": profiles[account_a]["post_count"],
                    "account_2_posts": profiles[account_b]["post_count"]
                })

    return profiles, matches
