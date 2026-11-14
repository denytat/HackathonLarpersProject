
import csv
from pathlib import Path
from datetime import datetime, timedelta

output = Path("data/processed/synthetic_organic.csv")
output.parent.mkdir(parents=True, exist_ok=True)

rows = []
start = datetime(2026, 11, 14, 12, 0)

# Fictional independent conversations
organic_messages = [
    "Does anyone know when the new library opens?",
    "I enjoyed the football match yesterday!",
    "The weather is beautiful today.",
    "Has anyone tried the new coffee shop?",
    "I'm looking forward to the weekend.",
    "The train was delayed again this morning.",
]

for i in range(30):
    rows.append({
        "id": f"organic_{i+1:03d}",
        "account": f"organic_user_{i+1:03d}",
        "text": organic_messages[i % len(organic_messages)],
        "timestamp": (
            start + timedelta(minutes=i * 20)
        ).isoformat(),
        "reply_to": "",
        "coordinated": "False",
        "techniques": "",
        "source": "synthetic_organic",
        "synthetic": "True",
        "campaign_id": "",
    })

# Fictional viral event: many independent reactions
viral_message = "The city museum announced free entry this weekend!"

for i in range(30):
    rows.append({
        "id": f"viral_{i+1:03d}",
        "account": f"viral_user_{i+1:03d}",
        "text": viral_message,
        "timestamp": (
            start + timedelta(hours=12, seconds=i * 12)
        ).isoformat(),
        "reply_to": "",
        "coordinated": "False",
        "techniques": "",
        "source": "synthetic_viral_hard_negative",
        "synthetic": "True",
        "campaign_id": "",
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

print(f"Created {len(rows)} synthetic organic posts")
print(f"Saved to: {output}")
