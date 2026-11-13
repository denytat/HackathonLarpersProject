
import json
from pathlib import Path
from unittest import result

from backend.detector import analyze_posts


# Project paths
ROOT = Path(__file__).resolve().parent.parent
POSTS_PATH = ROOT / "data" / "sample_posts_history.json"
LABELS_PATH = ROOT / "data" / "sample_labels.json"


def calculate_metrics(expected_accounts, predicted_accounts, all_accounts):
    expected = set(expected_accounts)
    predicted = set(predicted_accounts)
    all_accounts = set(all_accounts)

    tp = len(expected & predicted)
    fp = len(predicted - expected)
    fn = len(expected - predicted)
    tn = len(all_accounts - expected - predicted)

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )
    false_positive_rate = fp / (fp + tn) if fp + tn else 0

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": false_positive_rate
    }

def main():
    with open(POSTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Support both a plain list and {"posts": [...]}
    posts = data["posts"] if isinstance(data, dict) else data

    with open(LABELS_PATH, "r", encoding="utf-8") as file:
        labels = json.load(file)

    expected_accounts = labels["coordinated_accounts"]

    # Run the actual detector
    result = analyze_posts(posts)

    predicted_accounts = set()
    for swarm in result["swarms"]:
        predicted_accounts.update(swarm["accounts"])

    print("\nDetected swarms:")

    for swarm in result["swarms"]:
        print(f"\n{swarm['id']}")
        print("Accounts:", swarm["accounts"])
        print("Score:", swarm["score"])
        print("Evidence:")

        for edge in swarm["evidence"]:
            print(
                edge["account_1"],
                "<->",
                edge["account_2"],
                edge["signals"]
            )
    all_accounts = {post["account"] for post in posts}

    metrics = calculate_metrics(
        expected_accounts,
        predicted_accounts,
        all_accounts
    )

    print("\n========== SWARMWATCH EVALUATION ==========")

    print("\nExpected coordinated accounts:")
    print(sorted(expected_accounts))

    print("\nDetected accounts:")
    print(sorted(predicted_accounts))

    print("\nConfusion matrix:")
    for key in ["TP", "FP", "FN", "TN"]:
        print(f"{key}: {metrics[key]}")

    print("\nMetrics:")
    for key in ["precision", "recall", "f1", "false_positive_rate"]:
        print(f"{key}: {metrics[key]:.3f}")

    print("\n===========================================\n")


if __name__ == "__main__":
    main()
