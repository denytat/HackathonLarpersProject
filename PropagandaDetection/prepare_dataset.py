
import csv
from pathlib import Path
from datetime import datetime

# Input and output paths
input_folder = Path("data/raw/RussianTroll")
output_file = Path("data/processed/candidates.csv")

output_file.parent.mkdir(parents=True, exist_ok=True)

posts = []
seen_ids = set()

# Read all downloaded CSV files
for file in sorted(input_folder.glob("*.csv")):
    with open(file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            tweet_id = row.get("tweet_id", "").strip()
            text = row.get("content", "").strip()
            account = row.get("author", "").strip()

            if not tweet_id or not text or not account:
                continue

            if tweet_id in seen_ids:
                continue

            seen_ids.add(tweet_id)

            raw_date = row.get("publish_date", "").strip()
            try:
                timestamp = datetime.strptime(
                    raw_date, "%m/%d/%Y %H:%M"
                ).isoformat()
            except ValueError:
                timestamp = raw_date

            posts.append({
                "id": tweet_id,
                "account": account,
                "text": text,
                "timestamp": timestamp,
                "reply_to": "",
                "coordinated": "",
                "techniques": "",
                "source": "FiveThirtyEight_RussianTrollTweets",
            })

# Select up to 300 candidate posts
from collections import defaultdict
import random

random.seed(42)

# Group posts by account
by_account = defaultdict(list)

for post in posts:
    by_account[post["account"]].append(post)

# Select up to 10 posts per account
selected = []

for account, account_posts in by_account.items():
    random.shuffle(account_posts)
    selected.extend(account_posts[:10])

# Shuffle and keep up to 300 posts
random.shuffle(selected)
posts = selected[:300]

columns = [
    "id", "account", "text", "timestamp",
    "reply_to", "coordinated", "techniques", "source"
]

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(posts)

print(f"Created {output_file} with {len(posts)} candidate posts")
