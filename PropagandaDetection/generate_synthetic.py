
import csv
from pathlib import Path
from datetime import datetime, timedelta

output = Path("data/processed/synthetic_campaign.csv")
output.parent.mkdir(parents=True, exist_ok=True)

rows = []
start = datetime(2026, 11, 14, 10, 0)

messages = [
    "Urgent warning! The new policy will destroy our future!",
    "Urgent warning! This new policy will destroy our future!",
    "The new policy will destroy our future! Act now!",
    "Urgent! This policy threatens our future. Act now!",
]

for i in range(30):
    rows.append({
        "id": f"synthetic_{i+1:03d}",
        "account": f"synthetic_user_{i%10+1:02d}",
        "text": messages[i % len(messages)],
        "timestamp": (
            start + timedelta(seconds=i * 15)
        ).isoformat(),
        "reply_to": "",
        "coordinated": "True",
        "techniques": "loaded_language;fear_appeal",
        "source": "synthetic_campaign",
        "synthetic": "True",
        "campaign_id": "synthetic_campaign_001",
    })

columns = [
    "id", "account", "text", "timestamp",
    "reply_to", "coordinated", "techniques",
    "source", "synthetic", "campaign_id"
]

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Created {len(rows)} synthetic coordinated posts")
print(f"Saved to: {output}")
