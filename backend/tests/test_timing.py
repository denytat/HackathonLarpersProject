
import json
from pathlib import Path
from timing import find_timing_bursts

# Locate the project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load sample posts
DATA_PATH = PROJECT_ROOT / "data" / "sample_posts.json"

with open(DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

posts = data["posts"]

# Run timing detection
bursts = find_timing_bursts(
    posts,
    window_seconds=60,
    min_accounts=3
)

# Display results
print("\nTIMING BURSTS FOUND:\n")

for burst in bursts:
    print("Accounts:", ", ".join(burst["accounts"]))
    print("Posts:", ", ".join(burst["post_ids"]))
    print("Number of accounts:", burst["account_count"])
    print("Time:", burst["start_time"], "to", burst["end_time"])
    print("-" * 50)

print(f"\nTotal bursts found: {len(bursts)}")
