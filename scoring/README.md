# Scoring (§4.4)

Reads only Harbor's retained job outputs. Owner: Person E.

1. Build the trial table (`schema/trial-table.md`): one row per trial.
2. Harbor grades pass or fail (`reward.txt`). Scoring also extracts the reported values to compute normalized error: absolute difference from the published value divided by the tolerance.
3. Reliability metrics follow Rabanser et al. (2026): outcome and resource consistency over 3 repeats, paraphrase robustness, calibration error, AUROC and Brier score of stated confidence.
4. Variance split: crossed variance components for harness, model and paper.
