
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / "data" / "sample_posts.json"
OUTPUT_PATH = ROOT / "data" / "sample_posts_history.json"


def make_post(post_id, account, timestamp, text):
    return {
        "id": post_id,
        "account": account,
        "text": text,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "reply_to": None,
        "image_url": None
    }


def main():
    with open(SOURCE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    posts = data["posts"] if isinstance(data, dict) else data
    history = []

    # Coordinated-looking accounts:
    # Same posting hours and similar intervals.
    for account_number in range(1, 6):
        account = f"user{account_number:03d}"

        for day, hour in [(11, 7), (12, 8), (13, 9)]:
            timestamp = datetime(
                2026, 11, day, hour, 0,
                account_number * 5,
                tzinfo=timezone.utc
            )

            history.append(make_post(
                f"{account}_history_{day}",
                account,
                timestamp,
                "Daily update: sharing the latest developments."
            ))

    # Organic news accounts:
    # Different active hours for each account.
    news_hours = {
        11: [1, 6, 13],
        12: [2, 9, 17],
        13: [3, 11, 20],
        14: [4, 14, 21],
        15: [5, 15, 22]
    }

    for account_number, hours in news_hours.items():
        account = f"user{account_number:03d}"

        for index, hour in enumerate(hours):
            timestamp = datetime(
                2026, 11, 11 + index, hour, 20,
                account_number,
                tzinfo=timezone.utc
            )

            history.append(make_post(
                f"{account}_history_{index + 1}",
                account,
                timestamp,
                f"Personal news update number {index + 1}."
            ))

    # Organic music accounts:
    # Each account has a different activity schedule.
    music_hours = {
        16: [0, 8, 16],
        17: [1, 10, 18],
        18: [2, 12, 20]
    }

    for account_number, hours in music_hours.items():
        account = f"user{account_number:03d}"

        for index, hour in enumerate(hours):
            timestamp = datetime(
                2026, 11, 11 + index, hour, 35,
                account_number,
                tzinfo=timezone.utc
            )

            history.append(make_post(
                f"{account}_history_{index + 1}",
                account,
                timestamp,
                f"My music recommendation number {index + 1}."
            ))

    combined_posts = posts + history

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"posts": combined_posts},
            file,
            indent=4,
            ensure_ascii=False
        )

    print("Historical dataset created successfully.")
    print(f"Original posts: {len(posts)}")
    print(f"Historical posts added: {len(history)}")
    print(f"Total posts: {len(combined_posts)}")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
