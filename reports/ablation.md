# Ablation: what each stream adds (B2 LightGBM, seed 42, grouped 5-fold)

Window-level PR-AUC and AUROC on held-out participants; participant bootstrap (200) 95% CIs.
If a stream adds nothing, that is reported as a finding.

## Horizon 30 min

| Variant | n features | PR-AUC | AUROC |
|---|---|---|---|
| A0 glucose only | 15 | 0.399 [0.366, 0.432] | 0.908 [0.891, 0.922] |
| A1 +meals | 26 | 0.444 [0.389, 0.494] | 0.928 [0.913, 0.942] |
| A2 +wearable | 33 | 0.430 [0.373, 0.484] | 0.928 [0.913, 0.942] |
| A3 +static | 51 | 0.467 [0.407, 0.519] | 0.930 [0.915, 0.946] |
| A4 +personal (full twin) | 58 | 0.484 [0.427, 0.534] | 0.932 [0.914, 0.948] |
| Static only | 22 | 0.079 [0.060, 0.106] | 0.710 [0.649, 0.757] |
| Dynamic only | 33 | 0.430 [0.373, 0.484] | 0.928 [0.913, 0.942] |

## Horizon 60 min

| Variant | n features | PR-AUC | AUROC |
|---|---|---|---|
| A0 glucose only | 15 | 0.365 [0.323, 0.398] | 0.833 [0.810, 0.851] |
| A1 +meals | 26 | 0.424 [0.367, 0.466] | 0.868 [0.848, 0.885] |
| A2 +wearable | 33 | 0.416 [0.370, 0.463] | 0.866 [0.844, 0.884] |
| A3 +static | 51 | 0.450 [0.393, 0.496] | 0.870 [0.846, 0.889] |
| A4 +personal (full twin) | 58 | 0.455 [0.403, 0.500] | 0.875 [0.852, 0.898] |
| Static only | 22 | 0.148 [0.115, 0.192] | 0.721 [0.655, 0.767] |
| Dynamic only | 33 | 0.416 [0.370, 0.463] | 0.866 [0.844, 0.884] |

## Horizon 120 min

| Variant | n features | PR-AUC | AUROC |
|---|---|---|---|
| A0 glucose only | 15 | 0.426 [0.365, 0.480] | 0.784 [0.754, 0.810] |
| A1 +meals | 26 | 0.453 [0.393, 0.504] | 0.818 [0.794, 0.837] |
| A2 +wearable | 33 | 0.429 [0.375, 0.484] | 0.811 [0.784, 0.829] |
| A3 +static | 51 | 0.468 [0.390, 0.535] | 0.823 [0.791, 0.848] |
| A4 +personal (full twin) | 58 | 0.502 [0.432, 0.557] | 0.835 [0.803, 0.863] |
| Static only | 22 | 0.273 [0.215, 0.324] | 0.724 [0.658, 0.771] |
| Dynamic only | 33 | 0.429 [0.375, 0.484] | 0.811 [0.784, 0.829] |
