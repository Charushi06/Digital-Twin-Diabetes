# Metrics (held-out participants, grouped 5-fold CV x 3 seeds)

Threshold T = 180 mg/dL. 95% CIs from a participant-level bootstrap (100 resamples).
Participants: 45. Patient-days scored: 354.4.
Targets in the PRD are guidelines, not claims.

## Horizon 30 min

Eligible windows: 87089; positive: 3458 (3.97%).

| Model | AUROC | PR-AUC | Brier | ECE* | per-participant AUROC median (range) | event sensitivity @2/day | median lead (min) | alerts / patient-day |
|---|---|---|---|---|---|---|---|---|
| B0a | 0.847 [0.825, 0.870] | 0.254 [0.217, 0.291] | n/a | n/a | 0.824 (0.640 to 0.991) | 58.9% of 501 | 10 | 2.87 |
| B0b | 0.514 [0.509, 0.519] | 0.044 [0.034, 0.058] | n/a | n/a | 0.510 (0.490 to 0.547) | 0.0% of 501 | nan | 0.01 |
| B1 | 0.878 [0.840, 0.921] | 0.351 [0.306, 0.432] | 0.031 | 0.014 | 0.919 (0.703 to 0.997) | 52.7% of 501 | 10 | 1.97 |
| B2 | 0.936 [0.920, 0.951] | 0.481 [0.411, 0.539] | 0.027 | 0.005 | 0.942 (0.741 to 0.993) | 56.3% of 501 | 15 | 1.74 |

*ECE bins are sparse at high probabilities; read with caution.

Alert budget sweep (B2):

| budget/day | event sensitivity | median lead | alerts/patient-day |
|---|---|---|---|
| 1 | 35.5% | 10 | 0.73 |
| 2 | 56.5% | 15 | 1.79 |
| 4 | 59.1% | 15 | 3.98 |

Subgroups (B2):

| subgroup | participants | AUROC | PR-AUC |
|---|---|---|---|
| group=healthy | 15 | 0.946 [0.918, 0.969] | 0.313 [0.217, 0.409] |
| group=prediabetes | 16 | 0.940 [0.918, 0.960] | 0.510 [0.420, 0.578] |
| group=type2 | 14 | 0.901 [0.866, 0.936] | 0.521 [0.461, 0.584] |
| sex=female | 29 | 0.941 [0.926, 0.955] | 0.471 [0.387, 0.541] |
| sex=male | 16 | 0.927 [0.895, 0.951] | 0.497 [0.430, 0.563] |
| age>=65 | 2 | too few participants to report | |

## Horizon 60 min

Eligible windows: 86901; positive: 6534 (7.52%).

| Model | AUROC | PR-AUC | Brier | ECE* | per-participant AUROC median (range) | event sensitivity @2/day | median lead (min) | alerts / patient-day |
|---|---|---|---|---|---|---|---|---|
| B0a | 0.724 [0.702, 0.742] | 0.224 [0.192, 0.262] | n/a | n/a | 0.669 (0.509 to 0.937) | 85.6% of 501 | 15 | 4.78 |
| B0b | 0.518 [0.513, 0.521] | 0.087 [0.071, 0.112] | n/a | n/a | 0.521 (0.492 to 0.548) | 0.0% of 501 | nan | 0.01 |
| B1 | 0.789 [0.743, 0.849] | 0.330 [0.283, 0.390] | 0.060 | 0.022 | 0.793 (0.578 to 0.960) | 52.3% of 501 | 15 | 1.81 |
| B2 | 0.882 [0.861, 0.900] | 0.459 [0.388, 0.509] | 0.053 | 0.009 | 0.865 (0.640 to 0.981) | 61.9% of 501 | 20 | 1.73 |

*ECE bins are sparse at high probabilities; read with caution.

Alert budget sweep (B2):

| budget/day | event sensitivity | median lead | alerts/patient-day |
|---|---|---|---|
| 1 | 35.3% | 15 | 0.76 |
| 2 | 64.7% | 20 | 1.88 |
| 4 | 83.4% | 25 | 3.90 |

Subgroups (B2):

| subgroup | participants | AUROC | PR-AUC |
|---|---|---|---|
| group=healthy | 15 | 0.874 [0.828, 0.919] | 0.265 [0.172, 0.397] |
| group=prediabetes | 16 | 0.872 [0.841, 0.901] | 0.442 [0.340, 0.533] |
| group=type2 | 14 | 0.851 [0.816, 0.897] | 0.541 [0.495, 0.590] |
| sex=female | 29 | 0.890 [0.872, 0.908] | 0.449 [0.356, 0.525] |
| sex=male | 16 | 0.870 [0.828, 0.914] | 0.482 [0.422, 0.546] |
| age>=65 | 2 | too few participants to report | |

## Horizon 120 min

Eligible windows: 86536; positive: 12060 (13.94%).

| Model | AUROC | PR-AUC | Brier | ECE* | per-participant AUROC median (range) | event sensitivity @2/day | median lead (min) | alerts / patient-day |
|---|---|---|---|---|---|---|---|---|
| B0a | 0.624 [0.611, 0.639] | 0.234 [0.194, 0.284] | n/a | n/a | 0.601 (0.483 to 0.695) | 96.6% of 501 | 40 | 6.99 |
| B0b | 0.511 [0.509, 0.513] | 0.148 [0.121, 0.187] | n/a | n/a | 0.513 (0.500 to 0.521) | 0.0% of 501 | nan | 0.01 |
| B1 | 0.745 [0.690, 0.816] | 0.393 [0.322, 0.464] | 0.104 | 0.030 | 0.731 (0.483 to 0.842) | 49.7% of 501 | 65 | 2.17 |
| B2 | 0.839 [0.802, 0.867] | 0.507 [0.422, 0.565] | 0.092 | 0.013 | 0.824 (0.600 to 0.913) | 55.9% of 501 | 45 | 1.69 |

*ECE bins are sparse at high probabilities; read with caution.

Alert budget sweep (B2):

| budget/day | event sensitivity | median lead | alerts/patient-day |
|---|---|---|---|
| 1 | 32.1% | 30 | 0.78 |
| 2 | 54.7% | 45 | 1.71 |
| 4 | 78.2% | 70 | 3.61 |

Subgroups (B2):

| subgroup | participants | AUROC | PR-AUC |
|---|---|---|---|
| group=healthy | 15 | 0.797 [0.720, 0.874] | 0.278 [0.153, 0.458] |
| group=prediabetes | 16 | 0.810 [0.762, 0.853] | 0.451 [0.303, 0.565] |
| group=type2 | 14 | 0.818 [0.785, 0.856] | 0.622 [0.592, 0.666] |
| sex=female | 29 | 0.855 [0.830, 0.882] | 0.515 [0.399, 0.597] |
| sex=male | 16 | 0.814 [0.748, 0.879] | 0.505 [0.436, 0.576] |
| age>=65 | 2 | too few participants to report | |

Figures: `figures/pr_*.png`, `figures/calibration.png`.
Shipped model: B2 (LightGBM, monotone on ['glucose_now', 'last_meal_carbs', 'carbs_last_4h']). M1 fusion network not built (P1).