
import json
from pathlib import Path

from similarity import find_similar_posts
from timing import find_timing_bursts
from account_similarity import find_similar_accounts
from clustering import detect_swarms


# Load sample dataset
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "sample_posts.json"

with open(DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

posts = data["posts"]


# STEP 1: Text similarity
text_matches = find_similar_posts(
    posts,
    threshold=0.75
)


# STEP 2: Timing detection
timing_bursts = find_timing_bursts(
    posts,
    window_seconds=60,
    min_accounts=3
)


# STEP 3: Account behaviour similarity
profiles, account_matches = find_similar_accounts(
    posts,
    threshold=0.75,
    min_posts=2
)


# STEP 4: Graph clustering
swarms = detect_swarms(
    text_matches,
    timing_bursts,
    account_matches,
    min_signals=2,
    min_accounts=3
)


# Display results
print("\nTEXT MATCHES:", len(text_matches))
print("TIMING BURSTS:", len(timing_bursts))
print("ACCOUNT MATCHES:", len(account_matches))

print("\nPOTENTIAL SWARMS:\n")

for swarm in swarms:

    print("Swarm:", swarm["id"])
    print("Accounts:", ", ".join(swarm["accounts"]))
    print("Score:", swarm["score"])

    print("\nEvidence:")

    for item in swarm["evidence"]:
        print(
            f"{item['account_1']} <-> {item['account_2']} | "
            f"Score: {item['score']} | "
            f"Signals: {', '.join(item['signals'].keys())}"
        )

    print("-" * 60)

print(f"\nTotal potential swarms: {len(swarms)}")
