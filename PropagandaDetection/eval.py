
import argparse
import pandas as pd

def evaluate(ground_truth_file, predictions_file):
    truth = pd.read_csv(ground_truth_file)
    predictions = pd.read_csv(predictions_file)

    required_truth = {"id", "coordinated", "split"}
    required_pred = {"id", "predicted_coordinated"}

    if not required_truth.issubset(truth.columns):
        raise ValueError("Missing columns in ground truth CSV")

    if not required_pred.issubset(predictions.columns):
        raise ValueError("Missing columns in predictions CSV")

    if truth["id"].duplicated().any():
        raise ValueError("Duplicate IDs in ground truth")

    if predictions["id"].duplicated().any():
        raise ValueError("Duplicate IDs in predictions")

    # Evaluate only held-out examples
    truth = truth[truth["split"] == "eval"].copy()

    def parse_bool(value):
        if isinstance(value, bool):
            return value
        if str(value).strip().lower() == "true":
            return True
        if str(value).strip().lower() == "false":
            return False
        raise ValueError(f"Invalid boolean label: {value}")

    truth["coordinated"] = truth["coordinated"].map(parse_bool)
    predictions["predicted_coordinated"] = (
        predictions["predicted_coordinated"].map(parse_bool)
    )

    merged = truth.merge(
        predictions[["id", "predicted_coordinated"]],
        on="id",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    if (merged["_merge"] != "both").any():
        raise ValueError("Missing predictions for some evaluation posts")

    actual = merged["coordinated"]
    predicted = merged["predicted_coordinated"]

    tp = int((actual & predicted).sum())
    tn = int((~actual & ~predicted).sum())
    fp = int((~actual & predicted).sum())
    fn = int((actual & ~predicted).sum())

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )
    fpr = fp / (fp + tn) if fp + tn else 0

    print("\nSWARMWATCH EVALUATION")
    print("---------------------")
    print(f"Posts evaluated: {len(merged)}")
    print(f"True positives:  {tp}")
    print(f"True negatives:  {tn}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")
    print(f"Precision:       {precision:.3f}")
    print(f"Recall:          {recall:.3f}")
    print(f"F1 score:        {f1:.3f}")
    print(f"False-pos rate:  {fpr:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--truth", default="data/eval.csv"
    )
    parser.add_argument(
        "--predictions", required=True
    )
    args = parser.parse_args()
    evaluate(args.truth, args.predictions)
