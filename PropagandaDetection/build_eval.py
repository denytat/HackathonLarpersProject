
import csv
from pathlib import Path
from collections import Counter

data_dir = Path("data")
output = data_dir / "eval.csv"

inputs = [
    data_dir / "processed/synthetic_campaign.csv",
    data_dir / "processed/synthetic_organic.csv",
]

columns = [
    "id", "account", "text", "timestamp",
    "reply_to", "coordinated", "techniques",
    "source", "synthetic", "campaign_id",
    "split",
]

rows = []
seen_ids = set()

for path in inputs:
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            post_id = row["id"]

            if post_id in seen_ids:
                raise ValueError(f"Duplicate ID: {post_id}")

            seen_ids.add(post_id)

            # Keep the synthetic campaign entirely in evaluation.
            # These are demonstration splits, not a final benchmark.
            if row["source"] == "synthetic_campaign":
                split = "eval"
            elif row["source"] == "synthetic_viral_hard_negative":
                split = "eval"
            else:
                split = "dev"

            row["split"] = split
            rows.append(row)

with output.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(
        f, fieldnames=columns, extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {output}")
print(f"Total labeled posts: {len(rows)}")
print("Coordination labels:",
      dict(Counter(r["coordinated"] for r in rows)))
print("Splits:",
      dict(Counter(r["split"] for r in rows)))
