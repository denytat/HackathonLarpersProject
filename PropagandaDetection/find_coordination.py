
import pandas as pd
from difflib import SequenceMatcher

df = pd.read_csv("data/processed/candidates.csv")

df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce"
)

df = df.dropna(subset=["timestamp", "text", "account"])

matches = []

for i in range(len(df)):
    for j in range(i + 1, len(df)):
        a = df.iloc[i]
        b = df.iloc[j]

        # Coordination must involve different accounts
        if a["account"] == b["account"]:
            continue

        # Check whether posts are within 60 minutes
        minutes = abs(
            (a["timestamp"] - b["timestamp"]).total_seconds()
        ) / 60

        if minutes > 60:
            continue

        similarity = SequenceMatcher(
            None,
            str(a["text"]).lower(),
            str(b["text"]).lower()
        ).ratio()

        if similarity >= 0.8:
            matches.append({
                "account_1": a["account"],
                "account_2": b["account"],
                "post_1": a["id"],
                "post_2": b["id"],
                "minutes_apart": round(minutes, 2),
                "similarity": round(similarity, 3),
            })

result = pd.DataFrame(matches)

result.to_csv(
    "data/processed/coordination_candidates.csv",
    index=False
)

print("Potential coordination pairs:", len(matches))

if matches:
    print(result.head(10).to_string(index=False))
