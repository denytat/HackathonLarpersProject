# Synthetic Swarmwatch Dataset

## Overview

This dataset contains simulated social-media posts for testing the Swarmwatch coordination detector.

- Total accounts: 20
- Coordinated accounts: 5
- Organic accounts: 15
- Total posts: 25

## Coordinated accounts

Accounts user001-user005 are labeled as coordinated.

They publish identical messages within short time intervals. This simulates repetitive messaging and coordinated posting bursts.

## Organic accounts

Accounts user006-user020 are labeled as organic.

They discuss the same general topic but use different wording and post at different times.

This helps test whether the detector incorrectly identifies ordinary discussion as coordinated activity.

## Label assignment

All labels were assigned manually during synthetic dataset creation.

The labels are independent of Swarmwatch predictions.

## Limitations

This is a small synthetic dataset. It is useful for development and regression testing but cannot establish real-world detection accuracy.
