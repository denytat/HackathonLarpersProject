from datetime import datetime, timezone

def parse_timestamp(value):
    if isinstance(value, datetime):
        timestamp = value
    else:
        value = str(value).strip()

        # First try ISO format
        try:
            timestamp = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            # Try common CSV timestamp formats
            formats = [
                "%m/%d/%Y %H:%M",
                "%m/%d/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M"
            ]

            timestamp = None

            for fmt in formats:
                try:
                    timestamp = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue

            if timestamp is None:
                raise ValueError(
                    f"Unsupported timestamp format: {value}"
                )

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp



def find_timing_bursts(posts, window_seconds=60, min_accounts=3):
    """
    Find groups of different accounts posting within a short time window.

    window_seconds: maximum time between the first and last post
    min_accounts: minimum number of unique accounts required
    """

    if not posts:
        return []

    # Sort posts by timestamp
    sorted_posts = sorted(
        posts,
        key=lambda post: parse_timestamp(post["timestamp"])
    )

    bursts = []

    # Examine a time window starting at each post
    for i in range(len(sorted_posts)):
        start_time = parse_timestamp(
            sorted_posts[i]["timestamp"]
        )

        window_posts = []

        for post in sorted_posts[i:]:
            post_time = parse_timestamp(post["timestamp"])

            difference = (post_time - start_time).total_seconds()

            if difference > window_seconds:
                break

            window_posts.append(post)

        # Count unique accounts, not just the number of posts
        accounts = sorted({
            post["account"] for post in window_posts
        })

        if len(accounts) >= min_accounts:
            bursts.append({
                "accounts": accounts,
                "post_ids": [
                    post["id"] for post in window_posts
                ],
                "account_count": len(accounts),
                "post_count": len(window_posts),
                "start_time": start_time.isoformat(),
                "end_time": parse_timestamp(
                    window_posts[-1]["timestamp"]
                ).isoformat(),
                "window_seconds": window_seconds
            })

    return bursts
