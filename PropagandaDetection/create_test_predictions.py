
import pandas as pd
from pathlib import Path

# Load evaluation dataset
df = pd.read_csv("data/eval.csv")

# Only use evaluation split
df = df[df["split"] == "eval"].copy()

# Create dummy predictions matching the ground truth
df["predicted_coordinated"] = df["coordinated"]

# Deliberately flip 10 predictions to test metrics
n = min(10, len(df))
df.loc[df.index[:n], "predicted_coordinated"] = (
    ~df.loc[df.index[:n], "predicted_coordinated"].astype(bool)
)

# Save predictions
output = Path("data/processed/test_predictions.csv")

df[["id", "predicted_coordinated"]].to_csv(
    output, index=False
)

print(f"Created {len(df)} test predictions")
print(f"Saved to {output}")
