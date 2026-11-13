
import json
from pathlib import Path
from similarity import find_similar_posts

# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Build the path to sample_posts.json
DATA_PATH = PROJECT_ROOT / "data" / "sample_posts.json"

# Load the sample dataset
with open(DATA_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

posts = data["posts"]

# Run similarity detection
matches = find_similar_posts(posts)

# Print results
print("\nSIMILAR POSTS FOUND:\n")

for match in matches:
    print(
        f"{match['account_1']} and {match['account_2']} | "
        f"Similarity: {match['similarity']}"
    )

print(f"\nTotal matches: {len(matches)}")
