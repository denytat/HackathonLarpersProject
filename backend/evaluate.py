
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.detector import analyze_posts


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POSTS_PATH = ROOT / "data" / "synthetic" / "posts.csv"
DEFAULT_LABELS_PATH = ROOT / "data" / "synthetic" / "labels.json"
DEFAULT_REPORT_DIR = ROOT / "reports"


def load_dataset(posts_path, labels_path):
    """Load and validate a CSV dataset and its ground-truth labels."""

    with open(posts_path, "r", encoding="utf-8-sig", newline="") as file:
        non_empty_lines = (line for line in file if line.strip())
        reader = csv.DictReader(non_empty_lines)

        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

        required_columns = {
            "id", "account", "text", "timestamp",
            "reply_to", "image_url"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must contain columns: {sorted(required_columns)}"
            )

        posts = []

        for row in reader:
            row["reply_to"] = row["reply_to"] or None
            row["image_url"] = row["image_url"] or None

            if not row["id"] or not row["account"] or not row["text"]:
                raise ValueError(
                    f"Post has a missing required field: {row}"
                )

            posts.append(row)

    if not posts:
        raise ValueError("The dataset contains no posts.")

    post_ids = [post["id"] for post in posts]

    if len(post_ids) != len(set(post_ids)):
        raise ValueError("Duplicate post IDs found.")

    with open(labels_path, "r", encoding="utf-8") as file:
        labels = json.load(file)

    coordinated = set(labels["coordinated_accounts"])
    organic = set(labels["organic_accounts"])

    if coordinated & organic:
        raise ValueError(
            "An account cannot be both coordinated and organic."
        )

    all_accounts = {post["account"] for post in posts}
    labeled_accounts = coordinated | organic

    missing_labels = all_accounts - labeled_accounts
    unknown_labels = labeled_accounts - all_accounts

    if missing_labels:
        raise ValueError(
            f"Accounts missing ground-truth labels: {sorted(missing_labels)}"
        )

    if unknown_labels:
        raise ValueError(
            f"Labels reference accounts absent from CSV: {sorted(unknown_labels)}"
        )

    return posts, coordinated, all_accounts


def calculate_metrics(expected_accounts, predicted_accounts, all_accounts):
    expected = set(expected_accounts)
    predicted = set(predicted_accounts)
    all_accounts = set(all_accounts)

    tp = len(expected & predicted)
    fp = len((all_accounts - expected) & predicted)
    fn = len(expected - predicted)
    tn = len(all_accounts - expected - predicted)

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )

    false_positive_rate = fp / (fp + tn) if fp + tn else 0
    accuracy = (tp + tn) / len(all_accounts) if all_accounts else 0

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": false_positive_rate,
        "accuracy": accuracy,
    }


def save_report(report, report_path):
    """Save evaluation results as reproducible JSON."""

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate the Swarmwatch coordination detector."
    )

    parser.add_argument(
        "--posts",
        type=Path,
        default=DEFAULT_POSTS_PATH,
        help="Path to the posts CSV file."
    )

    parser.add_argument(
        "--labels",
        type=Path,
        default=DEFAULT_LABELS_PATH,
        help="Path to the ground-truth labels JSON file."
    )

    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path for the JSON evaluation report."
    )

    args = parser.parse_args()

    posts_path = args.posts
    labels_path = args.labels

    if not posts_path.is_absolute():
        posts_path = ROOT / posts_path

    if not labels_path.is_absolute():
        labels_path = ROOT / labels_path

    if args.report is None:
        report_path = (
            DEFAULT_REPORT_DIR /
            f"detector_evaluation_{posts_path.stem}.json"
        )
    else:
        report_path = args.report
        if not report_path.is_absolute():
            report_path = ROOT / report_path

    posts, expected_accounts, all_accounts = load_dataset(
        posts_path,
        labels_path
    )

    print(f"\nDataset: {posts_path.name}")
    print(f"Total posts: {len(posts)}")
    print(f"Total accounts: {len(all_accounts)}")
    print(f"Ground-truth coordinated accounts: {len(expected_accounts)}")
    print(
        "Ground-truth organic accounts: "
        f"{len(all_accounts - expected_accounts)}"
    )

    detection_result = analyze_posts(posts)

    predicted_accounts = set()

    for swarm in detection_result["swarms"]:
        predicted_accounts.update(swarm["accounts"])

    print("\nDetected swarms:")

    if not detection_result["swarms"]:
        print("No swarms detected.")

    for swarm in detection_result["swarms"]:
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

    for key in [
        "precision",
        "recall",
        "f1",
        "false_positive_rate",
        "accuracy"
    ]:
        print(f"{key}: {metrics[key]:.3f}")

    report = {
        "dataset": posts_path.stem,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posts_file": str(posts_path.relative_to(ROOT)),
        "labels_file": str(labels_path.relative_to(ROOT)),
        "total_posts": len(posts),
        "total_accounts": len(all_accounts),
        "ground_truth": {
            "coordinated_accounts": sorted(expected_accounts),
            "organic_accounts": sorted(all_accounts - expected_accounts)
        },
        "detected_swarms": detection_result["swarms"],
        "predicted_coordinated_accounts": sorted(predicted_accounts),
        "metrics": metrics
    }

    save_report(report, report_path)

    print("\n===========================================\n")


if __name__ == "__main__":
    main()
