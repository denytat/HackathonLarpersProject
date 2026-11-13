
from account_similarity import find_similar_accounts


# Separate test data: four posts per account
test_posts = [
    # Account A: posts every 30 minutes
    {"id": "a1", "account": "account_A", "text": "Post A1", "timestamp": "2026-11-14T09:00:00Z"},
    {"id": "a2", "account": "account_A", "text": "Post A2", "timestamp": "2026-11-14T09:30:00Z"},
    {"id": "a3", "account": "account_A", "text": "Post A3", "timestamp": "2026-11-14T10:00:00Z"},
    {"id": "a4", "account": "account_A", "text": "Post A4", "timestamp": "2026-11-14T10:30:00Z"},

    # Account B: almost the same posting pattern
    {"id": "b1", "account": "account_B", "text": "Post B1", "timestamp": "2026-11-14T09:05:00Z"},
    {"id": "b2", "account": "account_B", "text": "Post B2", "timestamp": "2026-11-14T09:35:00Z"},
    {"id": "b3", "account": "account_B", "text": "Post B3", "timestamp": "2026-11-14T10:05:00Z"},
    {"id": "b4", "account": "account_B", "text": "Post B4", "timestamp": "2026-11-14T10:35:00Z"},

    # Account C: very different posting pattern
    {"id": "c1", "account": "account_C", "text": "Post C1", "timestamp": "2026-11-14T14:00:00Z"},
    {"id": "c2", "account": "account_C", "text": "Post C2", "timestamp": "2026-11-14T18:00:00Z"},
    {"id": "c3", "account": "account_C", "text": "Post C3", "timestamp": "2026-11-14T22:00:00Z"},
    {"id": "c4", "account": "account_C", "text": "Post C4", "timestamp": "2026-11-15T02:00:00Z"},
]


profiles, matches = find_similar_accounts(
    test_posts,
    threshold=0.75,
    min_posts=2
)

print("\nACCOUNT PROFILES:\n")

for account, profile in profiles.items():
    print(account, profile)

print("\nSIMILAR ACCOUNT PAIRS:\n")

for match in matches:
    print(
        f"{match['account_1']} and {match['account_2']} | "
        f"Similarity: {match['similarity']}"
    )

print(f"\nTotal similar pairs: {len(matches)}")
