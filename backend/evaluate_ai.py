import argparse
import json
import os
import csv
from datetime import datetime, timezone
from pathlib import Path

from backend.phase2 import run_phase2


BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_TECHNIQUES = [
    "repetitive_messaging",
    "hashtag_spamming",
    "narrative_amplification",
    "emotional_manipulation",
    "impersonation",
    "misleading_claims",
]


def load_posts(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(
            line for line in file
            if line.strip()
        )

        posts = []
        for row in reader:
            if not row.get("id") or not row.get("text"):
                continue

            posts.append(row)

        return posts


def load_labels(path):
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def calculate_multilabel_metrics(expected, predicted):
    expected = set(expected)
    predicted = set(predicted)

    true_positive = len(expected & predicted)
    false_positive = len(predicted - expected)
    false_negative = len(expected - predicted)
    true_negative = len(
        set(ALLOWED_TECHNIQUES) - (expected | predicted)
    )

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else None
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else None
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None
        and recall is not None
        and precision + recall > 0
        else (0.0 if precision == 0 or recall == 0 else None)
    )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate_nemotron(result, labels):
    evaluated_ids = labels["evaluated_by_nemotron"]
    expected_labels = labels["post_labels"]

    result_by_id = {
        post["id"]: post
        for post in result["posts"]
    }

    predictions = {}
    missing_ids = []

    total_false_positives = 0
    total_decisions = 0

    for post_id in evaluated_ids:
        post = result_by_id.get(post_id)

        if post is None or not post.get("ai_analysis"):
            missing_ids.append(post_id)
            continue

        predicted = sorted({
            item["name"]
            for item in post.get("techniques", [])
        })

        expected = expected_labels[post_id]

        predictions[post_id] = {
            "expected": expected,
            "predicted": predicted,
            "correct": set(expected) == set(predicted),
            "ai_confidence": post["ai_analysis"]["confidence"],
            "explanation": post["ai_analysis"]["explanation"],
        }

        total_false_positives += len(
            set(predicted) - set(expected)
        )
        total_decisions += len(ALLOWED_TECHNIQUES)

    false_positive_rate = (
        total_false_positives / total_decisions
        if total_decisions else None
    )

    false_positive_posts = [
        post_id
        for post_id, item in predictions.items()
        if set(item["predicted"]) - set(item["expected"])
    ]

    return {
        "evaluated_posts": len(predictions),
        "missing_posts": missing_ids,
        "predictions": predictions,
        "false_positive_posts": false_positive_posts,
        "false_positive_technique_predictions": total_false_positives,
        "total_binary_decisions": total_decisions,
        "false_positive_rate": false_positive_rate,
        "precision_recall_f1": (
            "Not meaningful: all reviewed post-level labels are negative."
        ),
    }


def evaluate_gemini(result, labels):
    swarms = result.get("swarms", [])
    expected = labels["swarm_labels"]["expected_techniques"]

    if not swarms:
        return {
            "status": "no_swarm_detected",
            "expected": expected,
            "predicted": [],
            "metrics": None,
        }

    swarm_results = []

    for swarm in swarms:
        ai_analysis = swarm.get("ai_analysis") or {}
        gemini = ai_analysis.get("gemini")

        if not gemini:
            swarm_results.append({
                "swarm_id": swarm["id"],
                "status": ai_analysis.get("status", "unavailable"),
                "expected": expected,
                "predicted": [],
                "metrics": None,
            })
            continue

        predicted = gemini.get("techniques", [])

        swarm_results.append({
            "swarm_id": swarm["id"],
            "status": ai_analysis.get("status", "unknown"),
            "accounts": swarm.get("accounts", []),
            "expected": expected,
            "predicted": predicted,
            "metrics": calculate_multilabel_metrics(
                expected,
                predicted,
            ),
            "coordination_assessment": gemini.get(
                "coordination_assessment"
            ),
            "confidence": gemini.get("confidence"),
            "explanation": gemini.get("explanation"),
            "malicious_intent_established": labels[
                "swarm_labels"
            ]["malicious_intent_established"],
        })

    return {
        "number_of_detected_swarms": len(swarms),
        "results": swarm_results,
        "note": (
            "Gemini technique metrics are based on a single "
            "synthetic swarm and should not be treated as "
            "evidence of general real-world accuracy."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Nemotron and Gemini against human-reviewed labels."
    )

    parser.add_argument(
        "--posts",
        default="data/synthetic/challenge_posts.csv",
    )
    parser.add_argument(
        "--labels",
        default="data/synthetic/challenge_ai_labels.json",
    )
    parser.add_argument(
        "--output",
        default="reports/ai_evaluation_challenge.json",
    )

    args = parser.parse_args()

    posts_path = BASE_DIR / args.posts
    labels_path = BASE_DIR / args.labels
    output_path = BASE_DIR / args.output

    if not posts_path.exists():
        raise FileNotFoundError(posts_path)

    if not labels_path.exists():
        raise FileNotFoundError(labels_path)

    posts = load_posts(posts_path)
    labels = load_labels(labels_path)

    # Enable the existing Phase 2 AI pipeline.
    os.environ["ENABLE_AI"] = "true"

    print("Running Phase 2 with real AI providers...")
    print("Posts:", len(posts))

    result = run_phase2(posts)

    print("Evaluating Nemotron...")
    nemotron_report = evaluate_nemotron(result, labels)

    print("Evaluating Gemini...")
    gemini_report = evaluate_gemini(result, labels)

    report = {
        "dataset": labels["dataset"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posts_file": args.posts,
        "labels_file": args.labels,
        "ai_enabled": True,
        "detected_swarms": len(result.get("swarms", [])),
        "nemotron": nemotron_report,
        "gemini": gemini_report,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print("\n========== AI EVALUATION ==========")
    print("Nemotron evaluated posts:", nemotron_report["evaluated_posts"])
    print("Nemotron missing posts:", len(nemotron_report["missing_posts"]))
    print(
        "Nemotron false-positive posts:",
        len(nemotron_report["false_positive_posts"]),
    )
    print(
        "Nemotron false-positive rate:",
        nemotron_report["false_positive_rate"],
    )

    print("\nGemini swarm results:")
    for item in gemini_report.get("results", []):
        print("Swarm:", item["swarm_id"])
        print("Expected:", item["expected"])
        print("Predicted:", item["predicted"])
        print("Metrics:", item["metrics"])

    print("\nReport saved to:", output_path)


if __name__ == "__main__":
    main()
