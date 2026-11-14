
import csv
from collections import Counter
from pathlib import Path

path = Path("data/processed/candidates.csv")

with path.open(encoding="utf-8", newline="") as f:
    posts = list(csv.DictReader(f))

print("Total posts:", len(posts))

accounts = Counter(p["account"] for p in posts)
print("Unique accounts:", len(accounts))

print("\nTop 10 accounts:")
for account, count in accounts.most_common(10):
    print(f"{account}: {count} posts")

print("\nFirst 5 posts:")
for post in posts[:5]:
    print("\nAccount:", post["account"])
    print("Time:", post["timestamp"])
    print("Text:", post["text"][:200])
