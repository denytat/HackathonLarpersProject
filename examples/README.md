# Swarmwatch — Judge Example Datasets

All datasets in this folder are synthetic and created for demonstration and testing.

## Files

- coordinated_campaign.csv — a deliberately coordinated synthetic group alongside organic posts.
- organic_discussion.csv — independent users discussing a common broad topic.
- mixed_activity.csv — coordinated and organic activity in the same dataset.
- *_labels.json — reference labels describing the intended synthetic scenario.

## How to test

1. Open https://swarmspotter.tech
2. Upload one CSV dataset.
3. Run the analysis.
4. Review the coordination signals, grouped accounts, and AI-assisted explanations available in the interface.
5. Repeat with the other two datasets and compare the results.

API documentation: https://swarmspotter.tech/docs

## Important

The labels describe the datasets' intended construction. They are reference ground truth for a synthetic demonstration, not expected or guaranteed model outputs.

A detected similarity or coordination pattern is not proof of malicious intent. These examples do not represent real people, accounts, or campaigns.
